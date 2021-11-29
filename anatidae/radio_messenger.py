from PyQt5.QtCore import *
from utils import *
from generated import messages_pb2 as m


class RadioMessenger(QObject):

    robot_msg_sig = pyqtSignal(str, m.Message)

    def __init__(self, parent=None):
        super(RadioMessenger, self).__init__(parent)
