from PyQt5.QtCore import *
from utils import *


class Messenger(QObject):

    set_speed_sig = pyqtSignal(Speed)
    change_current_rid_sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super(Messenger, self).__init__(parent)

    def set_speed(self, speed: Speed):
        self.set_speed_sig.emit(speed)

    def change_current_rid(self, rid: str):
        self.change_current_rid_sig.emit(rid)
