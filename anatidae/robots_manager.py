from PyQt5.QtCore import *
from robot import *
from typing import Dict
from radio_sp import RadioSP
from messenger import Messenger


class RobotsManager(QObject):

    robot_pos_changed = pyqtSignal(str, Pos)
    robot_speed_changed = pyqtSignal(str, Speed)
    robot_bat_changed = pyqtSignal(str, float)

    def __init__(self, parent=None):
        super(RobotsManager, self).__init__(parent)
        self.robots = {}    # type: Dict[str, Robot]
        self.radiosp = RadioSP("/dev/ttyUSB0", 57600, self)
        self.connect_stuff(["pos", "speed", "bat"])
        self.radiosp.start()

    def stop(self):
        self.radiosp.stop()

    def connect_stuff(self, stuff_names):
        def update_pos(*args): self.update_stuff("pos", *args)
        def update_speed(*args): self.update_stuff("speed", *args)
        def update_bat(*args): self.update_stuff("bat", *args)

        getattr(self.radiosp, f"pos_changed").connect(update_pos)
        getattr(self.radiosp, f"speed_changed").connect(update_speed)
        getattr(self.radiosp, f"bat_changed").connect(update_bat)

    def update_stuff(self, stuff_name, rid, stuff):
        if rid not in self.robots:
            self.add_robot(rid, Robot(rid))
        getattr(self.robots[rid], f"set_{stuff_name}")(stuff)
        getattr(self, f"robot_{stuff_name}_changed").emit(rid, stuff)

    def add_robot(self, rid: str, r: Robot):
        self.robots[rid] = r

    def register_emiter(self, source: Messenger):
        source.set_speed.connect(lambda speed: self.radiosp.send_speed_cmd(speed))






