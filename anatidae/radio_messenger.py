from PyQt5.QtCore import *
from utils import *


class RadioMessenger(QObject):

    speed_changed = pyqtSignal(str, Speed)  # id, Speed
    pos_changed = pyqtSignal(str, Pos)  # id, Pos
    bat_changed = pyqtSignal(str, float)  # id, bat

    def __init__(self, parent=None):
        super(RadioMessenger, self).__init__(parent)
