from PyQt5.QtCore import *
from robot import *


class Messenger(QObject):

    set_speed = pyqtSignal(Speed)

    def __init__(self, parent=None):
        super(Messenger, self).__init__(parent)
