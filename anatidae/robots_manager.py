from PyQt5.QtCore import *
from robot import *
from typing import Dict
from messenger import Messenger
from abstract_radio import AbstractRadio


def foradio(func):
    def wrapped(self, *args):
        for radio in self.radios:
            func(self, radio, *args)
    return wrapped


class RobotsManager(QObject):

    robot_pos_changed = pyqtSignal(str, Pos)
    robot_speed_changed = pyqtSignal(str, Speed)
    robot_bat_changed = pyqtSignal(str, float)
    new_robot = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RobotsManager, self).__init__(parent)
        self.robots = {}    # type: Dict[str, Robot]
        self.radios = []
        self.current_rid = "NOP"

    def stop(self):
        for radio in self.radios:
            radio.stop()

    def add_radio(self, radio: AbstractRadio):
        self.radios.append(radio)
        self.connect_radio(radio)
        radio.start()

    def connect_radio(self, radio):
        def update_pos(*args): self.update_stuff("pos", *args)
        def update_speed(*args): self.update_stuff("speed", *args)
        def update_bat(*args): self.update_stuff("bat", *args)
        fcs = {"pos": update_pos, "speed": update_speed, "bat": update_bat}

        for name, func in fcs.items():
            getattr(radio.messenger, f"{name}_changed").connect(func)

    def update_stuff(self, stuff_name, rid, stuff):
        if rid not in self.robots:
            self.add_robot(rid, Robot(rid))
        getattr(self.robots[rid], f"set_{stuff_name}")(stuff)
        getattr(self, f"robot_{stuff_name}_changed").emit(rid, stuff)

    def add_robot(self, rid: str, r: Robot):
        self.robots[rid] = r
        self.new_robot.emit(rid)

    def register_emiter(self, source: Messenger):
        def send_speed_cmd(speed): self.send_stuff("speed_cmd", speed)
        def send_pid_gains(gains): self.send_stuff("pid_gains", gains)

        fcs = {"speed_cmd": send_speed_cmd, "pid_gains": send_pid_gains}

        for name, func in fcs.items():
            getattr(source, f"set_{name}_sig").connect(func)

        #getattr(source, f"set_speed_sig").connect(send_speed_cmd)
        #getattr(source, f"set_speed_sig").connect(send_pid_gains)

        source.change_current_rid_sig.connect(self.set_current_rid)

    def set_current_rid(self, rid):
        self.current_rid = rid

    @foradio
    def send_stuff(self, radio, stuffname, stuff):
        getattr(radio, f"send_{stuffname}")(self.current_rid, stuff)
