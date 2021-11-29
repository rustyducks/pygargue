from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from robot import *
from robots_manager import RobotsManager
from utils import *
from generated.arm_hat import Ui_ArmHat
from typing import Dict


class RAH(QWidget, Ui_ArmHat):
    def __init__(self, rid, robot_manager: RobotsManager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.rid = rid
        self.robot_manager = robot_manager

        self.arm1_initialized = False
        self.arm2_initialized = False
        self.hat_initialized = False

        self.arm1_traz.valueChanged.connect(lambda: self.send_arm_pos(1))
        self.arm1_rotz.valueChanged.connect(lambda: self.send_arm_pos(1))
        self.arm1_roty.valueChanged.connect(lambda: self.send_arm_pos(1))
        self.arm1_pump.toggled.connect(lambda: self.send_arm_pos(1))
        self.arm1_valve.toggled.connect(lambda: self.send_arm_pos(1))

        self.hat_valve.toggled.connect(self.send_hat_pos)
        self.hat_pump_checkbox.toggled.connect(self.send_hat_pos)
        self.hat_spinbox.valueChanged.connect(self.send_hat_pos)

    def handle_message(self, msg: m.Message):
        if msg.HasField("arm"):
            if msg.arm.arm_id == m.ARM1:
                self.set_arm1_state(msg)
            elif msg.arm.arm_id == m.ARM2:
                self.set_arm2_state(msg)
        elif msg.HasField("hat"):
            self.hat_valve_status.setChecked(msg.hat.valve)
            self.hat_pump_status.setChecked(msg.hat.pump)
            self.hat_pos_label.setText(f"{msg.hat.height}")

    def set_arm1_state(self, msg):
        self.arm1_pressureLabel.setText(f"pressure: {msg.arm.pressure}")
        self.pump1_status.setChecked(msg.arm.pump)
        self.valve1_status.setChecked(msg.arm.valve)
        self.traz1_label.setText(f"{msg.arm.traZ}")
        self.rotz1_label.setText(f"{msg.arm.rotZ}")
        self.roty1_label.setText(f"{msg.arm.rotY}")
        if not self.arm1_initialized:
            self.arm1_traz.setValue(msg.arm.traZ)
            self.arm1_roty.setValue(msg.arm.rotY)
            self.arm1_rotz.setValue(msg.arm.rotZ)
            self.arm1_pump.setChecked(msg.arm.pump)
            self.arm1_valve.setChecked(msg.arm.valve)
            self.arm1_initialized = True

    def set_arm2_state(self, msg):
        self.arm2_pressureLabel.setText(f"pressure: {msg.arm.pressure}")
        self.pump2_status.setChecked(msg.arm.pump)
        self.valve2_status.setChecked(msg.arm.valve)
        self.traz2_label.setText(f"{msg.arm.traZ}")
        self.rotz2_label.setText(f"{msg.arm.rotZ}")
        self.roty2_label.setText(f"{msg.arm.rotY}")
        if not self.arm2_initialized:
            self.arm2_traz.setValue(msg.arm.traZ)
            self.arm2_roty.setValue(msg.arm.rotY)
            self.arm2_rotz.setValue(msg.arm.rotZ)
            self.arm2_pump.setChecked(msg.arm.pump)
            self.arm2_valve.setChecked(msg.arm.valve)
            self.arm2_initialized = True

    def send_arm_pos(self, arm_id):
        msg = m.Message()
        msg.msg_type = m.Message.COMMAND
        msg.arm.arm_id = arm_id
        if arm_id == 1:
            msg.arm.arm_id = m.ARM1
            msg.arm.traZ = self.arm1_traz.value()
            msg.arm.rotZ = self.arm1_rotz.value()
            msg.arm.rotY = self.arm1_roty.value()
            msg.arm.pump = self.arm1_pump.isChecked()
            msg.arm.valve = self.arm1_valve.isChecked()
        elif arm_id == 2:
            msg.arm.arm_id = m.ARM2
            msg.arm.traZ = self.arm2_traz.value()
            msg.arm.rotZ = self.arm2_rotz.value()
            msg.arm.rotY = self.arm2_roty.value()
            msg.arm.pump = self.arm2_pump.isChecked()
            msg.arm.valve = self.arm2_valve.isChecked()
        self.robot_manager.send_msg(self.rid, msg)

    def send_hat_pos(self):
        msg = m.Message()
        msg.msg_type = m.Message.COMMAND
        msg.hat.height = self.hat_spinbox.value()
        msg.hat.pump = self.hat_pump_checkbox.isChecked()
        msg.hat.valve = self.hat_valve.isChecked()
        self.robot_manager.send_msg(self.rid, msg)

    def send_pump_cmd(self, pump, state):
        print(state)
        # self.messenger.set_pump_state(PumpCmd(pump, state))

