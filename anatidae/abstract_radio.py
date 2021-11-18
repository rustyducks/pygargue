
from radio_messenger import RadioMessenger
from utils import *
from logger import Logger


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

    # Up messages

    def emit_pos_changed(self, rid, pos: Pos):
        self.messenger.pos_changed.emit(rid, pos)

    def emit_speed_changed(self, rid, speed: Speed):
        self.messenger.speed_changed.emit(rid, speed)

    def emit_bat_changed(self, rid, bat: float):
        self.messenger.bat_changed.emit(rid, bat)

    # down messages

    def send_speed_cmd(self, rid, speed):
        raise NotImplementedError()

    def send_pid_gains(self, rid, gains):
        raise NotImplementedError()
