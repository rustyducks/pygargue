from PyQt5.QtCore import *
from utils import *


class Robot(QObject):

    def __init__(self, name, parent=None):
        super(Robot, self).__init__(parent)
        self.name = name
        self.pos = Pos(x=0, y=0, theta=0)
        self.speed = Speed(vx=0, vy=0, vtheta=0)
        self.bat = 0

    def set_pos(self, pos: Pos):
        self.pos = pos

    def set_speed(self, speed: Speed):
        self.speed = speed

    def set_bat(self, bat):
        self.bat = bat
