from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
from robot import *
import robots_manager
from typing import Optional
from utils import *
from math import cos, sin, pi
from enum import Enum
from generated import messages_pb2 as m


CMD_SPEED = 200
CMD_OMEGA = pi/2


ROBOT_SIZE = 30
ARROW_SIZE = 15
ARROW_ANGLE = pi + pi/8


class TableView(QWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.pix = QPixmap("data/map2022.png")
        self.robot_manager = None   # type: Optional[robots_manager.RobotsManager]
        self.speed_cmd = m.Message()
        self.speed_cmd.speed.vx = 0
        self.speed_cmd.speed.vy = 0
        self.speed_cmd.speed.vtheta = 0
        self.speed_cmd.msg_type = m.Message.COMMAND
        self.speed_timer = QTimer(self)
        self.speed_timer.timeout.connect(self.send_speed_command)
        self.speed_timer.start(200)

    def set_robot_manager(self, rman):
        self.robot_manager = rman  # type: robots_manager.RobotsManager
        self.robot_manager.robot_msg_sig.connect(self.update)
        # TODO keep current robot and stuff...

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 2))
        # paint background
        brush = QBrush()
        brush.setColor(QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        pix_ratio = self.pix.rect().width()/self.pix.rect().height()
        w_ratio = rect.width()/rect.height()

        if pix_ratio > w_ratio:
            w = rect.width()
            h = rect.width() / pix_ratio
            x = 0
            y = (rect.height() - h) / 2
        else:
            h = rect.height()
            w = rect.height() * pix_ratio
            x = (rect.width() - w) / 2
            y = 0
        pix_rect = QRect(int(x), int(y), int(w), int(h))
        painter.drawPixmap(pix_rect, self.pix, self.pix.rect())

        for rid, r in self.robot_manager.robots.items():
            pos = r.pos.pos
            xr = pos.x * w / 3000 + x
            yr = (2000 - pos.y) * h / 2000 + y
            painter.setBrush(Qt.red)
            center = QPoint(int(xr), int(yr))
            painter.drawEllipse(center, ROBOT_SIZE, ROBOT_SIZE)
            head = center + QPoint(ROBOT_SIZE * cos(-pos.theta), ROBOT_SIZE * sin(-pos.theta))
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(center, head)
            a1 = head + QPoint(ARROW_SIZE*cos(-pos.theta + ARROW_ANGLE), ARROW_SIZE*sin(-pos.theta + ARROW_ANGLE))
            a2 = head + QPoint(ARROW_SIZE * cos(-pos.theta - ARROW_ANGLE), ARROW_SIZE * sin(-pos.theta - ARROW_ANGLE))
            painter.setBrush(Qt.black)
            painter.drawPolygon(a1, head, a2)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.isAutoRepeat():
            return
        mult = 1
        if e.modifiers() & Qt.ShiftModifier:
            mult = 2
        if e.key() == Qt.Key_Z:
            self.speed_cmd.speed.vx = CMD_SPEED * mult
        elif e.key() == Qt.Key_S:
            self.speed_cmd.speed.vx = -CMD_SPEED * mult
        elif e.key() == Qt.Key_Q:
            self.speed_cmd.speed.vtheta = CMD_OMEGA * mult
        elif e.key() == Qt.Key_D:
            self.speed_cmd.speed.vtheta = -CMD_OMEGA * mult
        elif e.key() == Qt.Key_Shift:
            self.speed_cmd.speed.vx *= 2
            self.speed_cmd.speed.vtheta *= 2
        self.send_speed_command()

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if e.isAutoRepeat():
            return
        if e.key() == Qt.Key_Z:
            self.speed_cmd.speed.vx = 0
        elif e.key() == Qt.Key_S:
            self.speed_cmd.speed.vx = 0
        elif e.key() == Qt.Key_Q:
            self.speed_cmd.speed.vtheta = 0
        elif e.key() == Qt.Key_D:
            self.speed_cmd.speed.vtheta = 0
        elif e.key() == Qt.Key_Shift:
            self.speed_cmd.speed.vx /= 2
            self.speed_cmd.speed.vtheta /= 2
        self.send_speed_command()

    def send_speed_command(self):
        self.robot_manager.send_msg(self.robot_manager.current_rid, self.speed_cmd)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.setFocus()
        pass

