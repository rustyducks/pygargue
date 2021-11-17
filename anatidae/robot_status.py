from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from robot import *
import robots_manager
from messenger import Messenger
from utils import *
from generated.status import Ui_Status
from typing import Dict

class RStatus(QWidget, Ui_Status):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)


class RobotStatus(QTabWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.robot_manager = None
        self.tabs = {}  # type: Dict[RStatus]
        self.messenger = Messenger()
        self.currentChanged.connect(self.tab_changed)

    def set_robot_manager(self, rman):
        self.robot_manager = rman
        self.robot_manager.new_robot.connect(self.add_tab)
        self.robot_manager.robot_bat_changed.connect(self.update_bat)
        self.robot_manager.robot_pos_changed.connect(self.update_pos)
        self.robot_manager.robot_speed_changed.connect(self.update_speed)
        self.robot_manager.register_emiter(self.messenger)

    def tab_changed(self, tab_index: int):
        rid = self.tabText(tab_index)
        self.messenger.change_current_rid(rid)

    def add_tab(self, rid):
        rs = RStatus()
        self.tabs[rid] = rs
        self.addTab(rs, rid)
        self.messenger.change_current_rid(rid)
        rs.pid_gains_send_button.clicked.connect(lambda: self.send_pid_gains(rid))

    def send_pid_gains(self, rid):
        rs = self.tabs[rid]         # type: RStatus
        kp = rs.kp_spin.value()
        ki = rs.ki_spin.value()
        kd = rs.kd_spin.value()
        self.messenger.set_pid_gains(PidGains(kp, ki, kd))

    def update_bat(self, rid, bat):
        self.tabs[rid].bat_label.setText(f"{bat:.2f}")

    def update_pos(self, rid, pos: Pos):
        self.tabs[rid].x_label.setText(f"{pos.x:.2f}")
        self.tabs[rid].y_label.setText(f"{pos.y:.2f}")
        self.tabs[rid].theta_label.setText(f"{pos.theta:.2f}")

    def update_speed(self, rid, speed: Speed):
        self.tabs[rid].vx_label.setText(f"{speed.vx:.2f}")
        self.tabs[rid].vy_label.setText(f"{speed.vy:.2f}")
        self.tabs[rid].vtheta_label.setText(f"{speed.vtheta:.2f}")
