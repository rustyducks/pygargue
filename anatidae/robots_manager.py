from PyQt5.QtCore import *
from robot import *
from typing import Dict
from messenger import Messenger
from abstract_radio import AbstractRadio


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

        getattr(radio.messenger, f"pos_changed").connect(update_pos)
        getattr(radio.messenger, f"speed_changed").connect(update_speed)
        getattr(radio.messenger, f"bat_changed").connect(update_bat)

    def update_stuff(self, stuff_name, rid, stuff):
        if rid not in self.robots:
            self.add_robot(rid, Robot(rid))
        getattr(self.robots[rid], f"set_{stuff_name}")(stuff)
        getattr(self, f"robot_{stuff_name}_changed").emit(rid, stuff)

    def add_robot(self, rid: str, r: Robot):
        self.robots[rid] = r
        self.new_robot.emit(rid)

    def send_speed_cmd(self, speed):
        for radio in self.radios:
            radio.send_speed_cmd(self.current_rid, speed)

    def set_current_rid(self, rid):
        self.current_rid = rid

    def register_emiter(self, source: Messenger):
        source.set_speed_sig.connect(self.send_speed_cmd)
        source.change_current_rid_sig.connect(self.set_current_rid)

