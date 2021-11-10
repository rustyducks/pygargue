from PyQt5.QtCore import *


class RadioSP(QObject):
    """
    Radio protobuf over serial
    """

    #pos_changed = pyqtSignal(Pos)

    def __init__(self, parent=None):
        QObject.__init__(parent)
