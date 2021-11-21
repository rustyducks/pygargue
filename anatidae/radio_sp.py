import time
from PyQt5.QtCore import *
from serial import Serial
from enum import Enum
import struct
from generated import messages_pb2 as m

from google import protobuf
from robot import *
from utils import *
from abstract_radio import AbstractRadio, filter_sender
from logger import Logger


class RcvState(Enum):
    START1 = 0
    START2 = 1
    LEN = 2
    PAYLOAD_CHK = 3


class RadioSP(QThread, AbstractRadio):
    """
    Radio protobuf over serial
    """

    def __init__(self, port, baudrate, logger: Logger, rid="dafi", name="Ana", parent=None):
        super().__init__(logger=logger, parent=parent)
        self.serial = Serial(port, baudrate, timeout=0.01)
        self._rcv_state = RcvState.START1
        self._nb_bytes_expected = 1
        self.stop_requested = False
        self.rid = rid
        self.add_rid(rid)
        self.name = name

    def stop(self):
        print("stopping...")
        self.requestInterruption()
        while self.isRunning():
            time.sleep(0.001)
            pass
        self.serial.close()

    @staticmethod
    def compute_chk(payload):
        chk = 0
        for b in payload:
            chk ^= b
        return chk

    def check_msgs(self):
        while self.serial.in_waiting >= self._nb_bytes_expected:
            if self._rcv_state == RcvState.START1:  # wait for 0XFF
                if ord(self.serial.read()) == 0xFF:
                    self._rcv_state = RcvState.START2
                    self._nb_bytes_expected = 1
            elif self._rcv_state == RcvState.START2:
                if ord(self.serial.read()) == 0xFF:
                    self._rcv_state = RcvState.LEN
                    self._nb_bytes_expected = 1
                else:  # fallback to Idle
                    self._rcv_state = RcvState.START1
                    self._nb_bytes_expected = 1
            elif self._rcv_state == RcvState.LEN:
                self._nb_bytes_expected = ord(self.serial.read()) + 1  # expect 1 more byte for the checksum
                self._rcv_state = RcvState.PAYLOAD_CHK
            elif self._rcv_state == RcvState.PAYLOAD_CHK:
                payload = self.serial.read(self._nb_bytes_expected - 1)  # read message content
                chk = ord(self.serial.read())
                self._rcv_state = RcvState.START1
                if chk == self.compute_chk(payload):
                    msg = m.Message()
                    try:
                        msg.ParseFromString(payload)
                        return msg
                    except protobuf.message.DecodeError:
                        return None
                else:
                    print(f"chgk failed: {chk}  {self.compute_chk(payload)}")
                    return None

    def handle_umsg(self, msg):
        self.emit_msg(self.rid, msg)
        #if msg.HasField("bat") and msg.msg_type == m.Message.STATUS:

    @staticmethod
    def msg_to_dict(src, msg):
        msg_name = msg.WhichOneof('inner')
        inner = getattr(msg, msg_name)
        d_msg = {msg_name: {}}
        for f in inner.DESCRIPTOR.fields:
            field_name = f.name
            d_msg[msg_name][field_name] = getattr(inner, field_name)
        d = {src: d_msg}
        return d

    @filter_sender
    def send_msg(self, rid, msg: m.Message):
        payload = msg.SerializeToString()
        header = struct.pack("<BBB", 0xFF, 0xFF, len(payload))
        chk = struct.pack("<B", self.compute_chk(payload))
        data = header + payload + chk
        self.serial.write(data)
        self.serial.flushOutput()
        d = self.msg_to_dict(self.name, msg)
        self.log_dict(self.rid, d)
        # print(d)

    def run(self):
        while not self.isInterruptionRequested():
            time.sleep(0.001)
            msg = self.check_msgs()
            if msg is not None:
                self.handle_umsg(msg)
                d = self.msg_to_dict(self.rid, msg)
                self.log_dict(self.name, d)
