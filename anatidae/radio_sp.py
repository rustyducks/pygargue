import time
from PyQt5.QtCore import *
from serial import Serial
from enum import Enum
import struct
from generated import coinlang_down_pb2 as cld, coinlang_up_pb2 as clu
from google import protobuf
from robot import *
from utils import *
from abstract_radio import AbstractRadio, filter_sender
import socket
import json

plotjuggler_udp = ("127.0.0.1", 9870)


class RcvState(Enum):
    START1 = 0
    START2 = 1
    LEN = 2
    PAYLOAD_CHK = 3


class RadioSP(QThread, AbstractRadio):
    """
    Radio protobuf over serial
    """

    def __init__(self, port, baudrate, rid="dafi", parent=None):
        AbstractRadio.__init__(self)
        QThread.__init__(self, parent)
        self.serial = Serial(port, baudrate, timeout=0.01)
        self._rcv_state = RcvState.START1
        self._nb_bytes_expected = 1
        self.stop_requested = False
        self.rid = rid
        self.add_rid(rid)
        self.soplot = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
                    umsg = clu.UpMessage()
                    try:
                        umsg.ParseFromString(payload)
                        return umsg
                    except protobuf.message.DecodeError:
                        return None
                else:
                    print(f"chgk failed: {chk}  {self.compute_chk(payload)}")
                    return None

    def handle_umsg(self, u):
        if u.HasField("battery_report"):
            self.emit_bat_changed(self.rid, u.battery_report.voltage)
        elif u.HasField("pos_report"):
            self.emit_pos_changed(self.rid, Pos(u.pos_report.pos_x, u.pos_report.pos_y, u.pos_report.pos_theta))
        elif u.HasField("speed_report"):
            self.emit_speed_changed(self.rid, Speed(u.speed_report.vx, u.speed_report.vy, u.speed_report.vtheta))
        elif u.HasField("motor_report"):
            pass
            #print(f"motor report: {u.motor_report.m1} {u.motor_report.m2} {u.motor_report.m3}")
        else:
            print(u)

    def msg_to_json(self, msg):
        msg_name = msg.WhichOneof('inner')
        inner = getattr(msg, msg_name)
        d_msg = {msg_name: {}}
        for f in inner.DESCRIPTOR.fields:
            field_name = f.name
            d_msg[msg_name][field_name] = getattr(inner, field_name)
        d = {self.rid: d_msg}
        return json.dumps(d)

    def send_msg(self, msg):
        payload = msg.SerializeToString()
        header = struct.pack("<BBB", 0xFF, 0xFF, len(payload))
        chk = struct.pack("<B", self.compute_chk(payload))
        data = header + payload + chk
        self.serial.write(data)
        self.serial.flushOutput()

    @filter_sender
    def send_speed_cmd(self, rid, speed: Speed):
        msg = cld.DownMessage()
        msg.speed_command.vx = speed.vx
        msg.speed_command.vy = speed.vy
        msg.speed_command.vtheta = speed.vtheta
        self.send_msg(msg)

    @filter_sender
    def send_pid_gains(self, rid, gains: PidGains):
        msg = cld.DownMessage()
        msg.pid_gains.kp = gains.kp
        msg.pid_gains.ki = gains.ki
        msg.pid_gains.kd = gains.kd
        self.send_msg(msg)

    def run(self):
        while not self.isInterruptionRequested():
            time.sleep(0.001)
            msg = self.check_msgs()
            if msg is not None:
                self.handle_umsg(msg)
                j = self.msg_to_json(msg)
                self.soplot.sendto(j.encode(), plotjuggler_udp)
