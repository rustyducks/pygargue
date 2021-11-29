from enum import Enum
from generated import messages_pb2 as m
from google import protobuf
import struct


class RcvState(Enum):
    START1 = 0
    START2 = 1
    LEN = 2
    PAYLOAD = 3
    CHK = 4


class Transport:

    def __init__(self):
        self.payload_buffer = b''
        self.buffer = b''
        self._rcv_state = RcvState.START1
        self._nb_bytes_expected = 1

    @staticmethod
    def compute_chk(payload):
        chk = 0
        for b in payload:
            chk ^= b
        return chk

    def put(self, data: bytearray):
        self.buffer += data
        while len(self.buffer) > 0:
            nb, msg = self.advance(self.buffer)
            self.buffer = self.buffer[nb::]
            if msg is not None:
                # if len(self.buffer) == 0:
                #     print("transport buffer OK!")
                return msg
        return None

    def advance(self, data):
        b = data[0]
        if self._rcv_state == RcvState.START1:  # wait for 0XFF
            if b == 0xFF:
                self._rcv_state = RcvState.START2
            return 1, None
        elif self._rcv_state == RcvState.START2:
            if b == 0xFF:
                self._rcv_state = RcvState.LEN
            else:  # fallback to Idle
                self._rcv_state = RcvState.START1
            return 1, None
        elif self._rcv_state == RcvState.LEN:
            self._nb_bytes_expected = b
            self._rcv_state = RcvState.PAYLOAD
            self.payload_buffer = b''
            return 1, None
        elif self._rcv_state == RcvState.PAYLOAD:
            dlen = min(len(data), self._nb_bytes_expected)
            self.payload_buffer += data[:dlen]
            self._nb_bytes_expected -= dlen
            if self._nb_bytes_expected == 0:
                self._rcv_state = RcvState.CHK
            return dlen, None
        elif self._rcv_state == RcvState.CHK:
            chk = b
            self._rcv_state = RcvState.START1
            if chk == self.compute_chk(self.payload_buffer):
                msg = m.Message()
                try:
                    msg.ParseFromString(self.payload_buffer)
                    return 1, msg
                except protobuf.message.DecodeError:
                    return 1, None
            else:
                print(f"chgk failed: {chk}  {self.compute_chk(self.payload_buffer)}")
                return 1, None

    def serialize(self, msg):
        payload = msg.SerializeToString()
        header = struct.pack("<BBB", 0xFF, 0xFF, len(payload))
        chk = struct.pack("<B", self.compute_chk(payload))
        data = header + payload + chk
        return data