from PyQt5.QtCore import *
from robot import *
from typing import Dict, List
from abstract_radio import AbstractRadio
from generated import messages_pb2 as m


class RobotsManager(QObject):

    robot_msg_sig = pyqtSignal(str, m.Message)
    new_robot_sig = pyqtSignal(str)
    change_current_rid_sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RobotsManager, self).__init__(parent)
        self.robots = {}    # type: Dict[str, Robot]
        self.radios = []    # type: List[AbstractRadio]
        self.current_rid = "NOP"

    def stop(self):
        for radio in self.radios:
            radio.stop()

    def add_radio(self, radio: AbstractRadio):
        self.radios.append(radio)
        radio.messenger.robot_msg_sig.connect(self.handle_msg)
        radio.start()

    def add_robot(self, rid):
        r = Robot(rid)
        self.robots[rid] = r
        self.new_robot_sig.emit(rid)

    def set_current_rid(self, rid):
        self.current_rid = rid
        self.change_current_rid_sig.emit(rid)

    def handle_msg(self, src, msg: m.Message):
        if src not in self.robots:
            self.add_robot(src)
        self.robots[src].handle_msg(msg)
        self.robot_msg_sig.emit(src, msg)

    def send_msg(self, dst, msg: m.Message):
        for radio in self.radios:
            if dst in radio.rids:
                radio.send_msg(dst, msg)
