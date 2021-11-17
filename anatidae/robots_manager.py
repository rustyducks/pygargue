from PyQt5.QtCore import *
from robot import *
from typing import Dict
from radio_sp import RadioSP
from messenger import Messenger


class RobotsManager(QObject):

    robot_pos_changed = pyqtSignal(str, Pos)
    robot_bat_changed = pyqtSignal(str, float)

    def __init__(self, parent=None):
        super(RobotsManager, self).__init__(parent)
        self.robots = {}    # type: Dict[str, Robot]
        self.radiosp = RadioSP("/dev/bmp_tty", 115200, self)
        self.radiosp.pos_changed.connect(self.update_pos)
        self.radiosp.bat_changed.connect(self.update_bat)
        self.radiosp.start()

    def stop(self):
        self.radiosp.stop()

    def update_pos(self, rid, pos: Pos):
        if rid not in self.robots:
            self.add_robot(rid, Robot(rid))
        self.robots[rid].set_pos(pos.x, pos.y, pos.theta)
        self.robot_pos_changed.emit(rid, pos)

    def update_bat(self, rid, bat):
        if rid not in self.robots:
            self.add_robot(rid, Robot(rid))
        self.robots[rid].set_bat(bat)
        self.robot_bat_changed.emit(rid, bat)

    def add_robot(self, rid: str, r: Robot):
        self.robots[rid] = r

    def register_emiter(self, source: Messenger):
        source.set_speed.connect(lambda speed: self.radiosp.send_speed_cmd(speed))






