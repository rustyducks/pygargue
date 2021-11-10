from PyQt5.QtCore import *
from collections import namedtuple

Pos = namedtuple('Pos', ['x', 'y', 'theta'])
Speed = namedtuple('Speed', ['vx', 'vy', 'vtheta'])


class Robot(QObject):

    pos_changed = pyqtSignal(Pos)

    def __init__(self, name, parent=None):
        QObject.__init__(parent)
        self.name = name
        self.pos = Pos(x=0, y=0, theta=0)
        self.speed = Speed(vx=0, vy=0, vtheta=0)

    def set_pos(self, pos: Pos):
        self.pos = pos
        self.pos_changed.emit(self.pos)

