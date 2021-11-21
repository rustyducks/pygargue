from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from robot import *
from robots_manager import RobotsManager
from utils import *
from generated.status import Ui_Status
from typing import Dict


class RobotStatus(QWidget, Ui_Status):
    def __init__(self, rid, robot_manager: RobotsManager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.rid = rid
        self.robot_manager = robot_manager
        # self.pid_gains_send_button.clicked.connect(lambda: self.send_pid_gains(rid))

    def handle_message(self, msg: m.Message):
        if msg.HasField("pos") and msg.msg_type == m.Message.STATUS:
            self.update_pos(msg)
        elif msg.HasField("speed") and msg.msg_type == m.Message.STATUS:
            self.update_speed(msg)
        elif msg.HasField("bat") and msg.msg_type == m.Message.STATUS:
            self.update_bat(msg)

    def send_pid_gains(self, rid):
        pid_no = int(self.pid_no_combo.currentText())
        feedforward = self.ng_spin.value()
        kp = self.kp_spin.value()
        ki = self.ki_spin.value()
        kd = self.kd_spin.value()
        msg = m.Message()
        msg.motor_pid.motor_no = pid_no
        msg.motor_pid.feedforward = feedforward
        msg.motor_pid.kp = kp
        msg.motor_pid.ki = ki
        msg.motor_pid.kd = kd
        self.robot_manager.send_msg(self.rid, msg)

    def update_bat(self, msg):
        bat = msg.bat
        self.bat_label.setText(f"{bat.voltage:.2f}")

    def update_pos(self, msg: m.Message):
        pos = msg.pos
        self.x_label.setText(f"{pos.x:.2f}")
        self.y_label.setText(f"{pos.y:.2f}")
        self.theta_label.setText(f"{pos.theta:.2f}")

    def update_speed(self, msg: m.Message):
        speed = msg.speed
        self.vx_label.setText(f"{speed.vx:.2f}")
        self.vy_label.setText(f"{speed.vy:.2f}")
        self.vtheta_label.setText(f"{speed.vtheta:.2f}")
