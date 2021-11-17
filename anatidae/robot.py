from PyQt5.QtCore import *
from collections import namedtuple
from utils import *


class Robot(QObject):

    def __init__(self, name, parent=None):
        super(Robot, self).__init__(parent)
        self.name = name
        self.pos = Pos(x=0, y=0, theta=0)
        self.speed = Speed(vx=0, vy=0, vtheta=0)
        self.bat = 0

    def set_pos(self, x, y, theta):
        self.pos = Pos(x=x, y=y, theta=theta)

    def set_bat(self, bat):
        self.bat = bat
