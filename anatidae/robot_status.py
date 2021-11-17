from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from robot import *
import robots_manager
from messenger import Messenger
from utils import *
from generated.status import Ui_Status


class RobotStatus(QWidget, Ui_Status):

    def __init__(self, rman: robots_manager.RobotsManager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        #self.robot_manager = rman
        self.robot_manager = None
        self.setupUi(self)
        #self.robot_manager.robot_bat_changed.connect(self.update_bat)
        #self.robot_manager.robot_pos_changed.connect(self.update_pos)

    def set_robot_manager(self, rman):
        self.robot_manager = rman
        self.robot_manager.robot_bat_changed.connect(self.update_bat)
        self.robot_manager.robot_pos_changed.connect(self.update_pos)
        self.robot_manager.robot_speed_changed.connect(self.update_speed)

    def update_bat(self, rid, bat):
        self.bat_label.setText(f"{bat:.2f}")

    def update_pos(self, rid, pos: Pos):
        self.x_label.setText(f"{pos.x:.2f}")
        self.y_label.setText(f"{pos.y:.2f}")
        self.theta_label.setText(f"{pos.theta:.2f}")

    def update_speed(self, rid, speed: Speed):
        self.vx_label.setText(f"{speed.vx:.2f}")
        self.vy_label.setText(f"{speed.vy:.2f}")
        self.vtheta_label.setText(f"{speed.vtheta:.2f}")
