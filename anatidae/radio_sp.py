import time
from serial import Serial
from robot import *
from abstract_radio import AbstractRadio, filter_sender
from logger import Logger
from transport import Transport


class RadioSP(QThread, AbstractRadio):
    """
    Radio protobuf over serial
    """

    def __init__(self, port, baudrate, logger: Logger, rid="dafi", name="Ana", parent=None):
        super().__init__(logger=logger, parent=parent)
        self.serial = Serial(port, baudrate, timeout=0.01)
        self.transport = Transport()
        self.stop_requested = False
        self.rid = rid
        self.add_rid(rid)
        self.name = name

    def stop(self):
        print("stopping...")
        self.requestInterruption()
        while self.isRunning():
            time.sleep(0.01)
            pass
        self.serial.close()

    def check_msgs(self):
        data = self.serial.read(self.serial.in_waiting)
        msg = self.transport.put(data)
        return msg

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
        data = self.transport.serialize(msg)
        self.serial.write(data)
        self.serial.flushOutput()
        d = self.msg_to_dict(self.name, msg)
        self.log_dict(self.rid, d)
        # print(d)

    def run(self):
        self.emit_msg(self.rid, m.Message())
        while not self.isInterruptionRequested():
            time.sleep(0.001)
            msg = self.check_msgs()
            if msg is not None:
                self.handle_umsg(msg)
                d = self.msg_to_dict(self.rid, msg)
                self.log_dict(self.name, d)
