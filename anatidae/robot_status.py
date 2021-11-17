from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from robot import *
import robots_manager
from messenger import Messenger
from utils import *
from math import cos, sin, pi
from generated.status import Ui_Status

CMD_SPEED = 100
CMD_OMEGA = 0.2


ROBOT_SIZE = 30
ARROW_SIZE = 15
ARROW_ANGLE = pi + pi/8


class RobotStatus(QWidget, Ui_Status):

    def __init__(self, rman: robots_manager.RobotsManager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.robot_manager = rman
        self.setupUi(self)
        self.robot_manager.robot_bat_changed.connect(self.update_bat)
        self.robot_manager.robot_pos_changed.connect(self.update_pos)

    def update_bat(self, rid, bat):
        self.bat_label.setText(f"{bat:.2f}")

    def update_pos(self, rid, pos: Pos):
        self.pos_label.setText(f"X:{pos.x:.2f}, Y:{pos.y:.2f}, Theta:{pos.theta:.2f}")

