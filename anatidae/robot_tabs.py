from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from robot import *
import robots_manager
from typing import Optional, Dict
from robot_status import RobotStatus
from arm_hat import RAH

class RobotTab(QWidget):
    def __init__(self, rid, robot_manager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.rid = rid
        lay = QHBoxLayout(self)
        self.robot_status = RobotStatus(rid=rid, robot_manager=robot_manager, parent=self)
        lay.addWidget(self.robot_status)
        self.rah = RAH(rid=rid, robot_manager=robot_manager, parent=self)
        lay.addWidget(self.rah)

    def handle_msg(self, msg: m.Message):
        self.robot_status.handle_message(msg)
        self.rah.handle_message(msg)


class RobotTabs(QTabWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.robot_manager = None   # type: Optional[robots_manager.RobotsManager]
        self.tabs = {}      # type: Dict[str, RobotTab]
        self.currentChanged.connect(self.tab_changed)

    def set_robot_manager(self, rman: robots_manager.RobotsManager):
        self.robot_manager = rman
        self.robot_manager.new_robot_sig.connect(self.add_tab)
        self.robot_manager.robot_msg_sig.connect(self.handle_message)

    def tab_changed(self, tab_index: int):
        rid = self.tabText(tab_index)
        self.robot_manager.set_current_rid(rid)

    def add_tab(self, rid):
        tab = RobotTab(rid=rid, robot_manager=self.robot_manager, parent=self)
        self.addTab(tab, rid)
        self.tabs[rid] = tab
        self.robot_manager.set_current_rid(rid)

    def handle_message(self, rid, msg: m.Message):
        self.tabs[rid].handle_msg(msg)


