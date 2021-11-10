#!/usr/bin/python3
from serial import Serial
from enum import Enum
import struct
import time
from generated import coinlang_down_pb2 as cld, coinlang_up_pb2 as clu
from google import protobuf
import json
import socket
import sys

plotjuggler_udp = ("127.0.0.1", 9870)


class RcvState(Enum):
    START1 = 0
    START2 = 1
    LEN = 2
    PAYLOAD_CHK = 3


class SerialCom:

    def __init__(self, port, baudrate=115200):
        self.serial = Serial(port, baudrate, timeout=0.01)
        self._rcv_state = RcvState.START1
        self._nb_bytes_expected = 1

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
            print(f"battery_report: {u.battery_report.voltage}")
        elif u.HasField("pos_report"):
            print(f"pos report: {u.pos_report.pos_x:.2f} {u.pos_report.pos_y:.2f} {u.pos_report.pos_theta:.2f}")
        elif u.HasField("speed_report"):
            print(f"speed report: {u.speed_report.vx:.2f} {u.speed_report.vy:.2f} {u.speed_report.vtheta:.2f}")
        elif u.HasField("motor_report"):
            print(f"motor report: {u.motor_report.m1} {u.motor_report.m2} {u.motor_report.m3}")
        else:
            print(u)

    def msg_to_json(self, msg):
        msg_name = msg.WhichOneof('inner')
        inner = getattr(msg, msg_name)
        d = {msg_name: {}}
        for f in inner.DESCRIPTOR.fields:
            field_name = f.name
            d[msg_name][field_name] = getattr(inner, field_name)
        return json.dumps(d)

    def send_msg(self, msg):
        payload = msg.SerializeToString()
        header = struct.pack("<BBB", 0xFF, 0xFF, len(payload))
        chk = struct.pack("<B", self.compute_chk(payload))
        data = header + payload + chk
        print(data)
        self.serial.write(data)

    def send_speed_cmd(self, vx, vy, vtheta):
        msg = cld.DownMessage()
        msg.speed_command.vx = vx
        msg.speed_command.vy = vy
        msg.speed_command.vtheta = vtheta
        self.send_msg(msg)


if __name__ == "__main__":

    port = sys.argv[1] if len(sys.argv) >= 2 else "/dev/bmp_tty"
    baudrate = int(sys.argv[2]) if len(sys.argv) >= 3 else 115200

    com = SerialCom(port, baudrate)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        msg = com.check_msgs()
        if msg is not None:
            j = com.msg_to_json(msg)
            print(j)
            s.sendto(j.encode(), plotjuggler_udp)
