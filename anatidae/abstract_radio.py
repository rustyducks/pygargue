
from radio_messenger import RadioMessenger
from utils import *
from logger import Logger
from generated import messages_pb2 as m

STATUS = m.Message.STATUS
COMMAND = m.Message.COMMAND


def filter_sender(func):
    """
    decorator filtering messages to be sent by rid.
    The function is called only if rid is known.
    """
    def wrapped(self, rid, *args):
        if rid in self.rids:
            func(self, rid, *args)
    return wrapped


class AbstractRadio:

    def __init__(self, logger: Logger, **kwargs):
        super(AbstractRadio, self).__init__(**kwargs)
        self.messenger = RadioMessenger()
        self.rids = []
        self.logger = logger    # type: Logger

    def add_rid(self, rid):
        self.rids.append(rid)

    def log_dict(self, dst, d):
        self.logger.log_dict(dst, d)

    def start(self):
        raise NotImplementedError("The start method must be implemented!")

    def stop(self):
        raise NotImplementedError("The stop method must be implemented!")

    def emit_msg(self, src, msg: m.Message):
        self.messenger.robot_msg_sig.emit(src, msg)

    def send_msg(self, dst, msg: m.Message):
        raise NotImplementedError("you must implement send_msg method!!!")
