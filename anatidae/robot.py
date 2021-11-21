from PyQt5.QtCore import *
from utils import *
from generated import messages_pb2 as m


class Robot:
    """
    store robot state
    """
    def __init__(self, rid):
        self.rid = rid
        self.pos = m.Message()
        self.speed = m.Message()
        self.bat = m.Message()

    def handle_msg(self, msg: m.Message):
        if msg.HasField("pos") and msg.msg_type == m.Message.STATUS:
            self.pos = msg
        elif msg.HasField("speed") and msg.msg_type == m.Message.STATUS:
            self.speed = msg
        elif msg.HasField("bat") and msg.msg_type == m.Message.STATUS:
            self.bat = msg
        else:
            pass
            # TODO: save other messages
