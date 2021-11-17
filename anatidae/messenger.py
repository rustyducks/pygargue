from PyQt5.QtCore import *
from utils import *


class Messenger(QObject):

    set_speed_cmd_sig = pyqtSignal(Speed)
    set_pid_gains_sig = pyqtSignal(PidGains)
    change_current_rid_sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super(Messenger, self).__init__(parent)

    def set_speed_cmd(self, speed: Speed):
        self.set_speed_cmd_sig.emit(speed)

    def change_current_rid(self, rid: str):
        self.change_current_rid_sig.emit(rid)

    def set_pid_gains(self, gains):
        self.set_pid_gains_sig.emit(gains)
