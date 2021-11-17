
from radio_messenger import RadioMessenger
from utils import *


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

    def __init__(self):
        self.messenger = RadioMessenger()
        self.rids = []

    def add_rid(self, rid):
        self.rids.append(rid)

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
