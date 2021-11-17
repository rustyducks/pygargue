import time

from PyQt5.QtCore import *
from serial import Serial
from enum import Enum
import struct
from generated import coinlang_down_pb2 as cld, coinlang_up_pb2 as clu
from google import protobuf
from robot import *
from utils import *

class RcvState(Enum):
    START1 = 0
    START2 = 1
    LEN = 2
    PAYLOAD_CHK = 3


class RadioSP(QThread):
    """
    Radio protobuf over serial
    """

    pos_changed = pyqtSignal(str, Pos)  # id, Pos
    bat_changed = pyqtSignal(str, float)  # id, bat

    def __init__(self, port, baudrate, parent=None):
        super(RadioSP, self).__init__(parent)
        self.serial = Serial(port, baudrate, timeout=0.01)
        self._rcv_state = RcvState.START1
        self._nb_bytes_expected = 1
        self.stop_requested = False

    def stop(self):
        self.requestInterruption()
        while self.isRunning():
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
            self.bat_changed.emit("dafi", u.battery_report.voltage)
            #print(f"battery_report: {u.battery_report.voltage}")
        elif u.HasField("pos_report"):
            pass
            #print(f"pos report: {u.pos_report.pos_x:.2f} {u.pos_report.pos_y:.2f} {u.pos_report.pos_theta:.2f}")
            self.pos_changed.emit("dafi", Pos(u.pos_report.pos_x, u.pos_report.pos_y, u.pos_report.pos_theta))
        elif u.HasField("speed_report"):
            pass
            #print(f"speed report: {u.speed_report.vx:.2f} {u.speed_report.vy:.2f} {u.speed_report.vtheta:.2f}")
        elif u.HasField("motor_report"):
            pass
            #print(f"motor report: {u.motor_report.m1} {u.motor_report.m2} {u.motor_report.m3}")
        else:
            print(u)

    def send_msg(self, msg):
        payload = msg.SerializeToString()
        header = struct.pack("<BBB", 0xFF, 0xFF, len(payload))
        chk = struct.pack("<B", self.compute_chk(payload))
        data = header + payload + chk
        self.serial.write(data)

    def send_speed_cmd(self, speed: Speed):
        msg = cld.DownMessage()
        msg.speed_command.vx = speed.vx
        msg.speed_command.vy = speed.vy
        msg.speed_command.vtheta = speed.vtheta
        self.send_msg(msg)

    def run(self):
        while not self.isInterruptionRequested():
            time.sleep(0.001)
            msg = self.check_msgs()
            if msg is not None:
                self.handle_umsg(msg)

