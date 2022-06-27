from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
from robot import *
import robots_manager
from typing import Optional
from utils import *
from math import cos, sin, pi, atan2
from enum import Enum
from generated import messages_pb2 as m


CMD_SPEED = 200
CMD_OMEGA = pi/2


ROBOT_SIZE = 30
ARROW_SIZE = 15
ARROW_ANGLE = pi + pi/8

POS_ORIENT_THRESHOLD = 20


class TableView(QWidget):

    mouse_pos_changed = pyqtSignal(int, int)
    pos_cmd_changed = pyqtSignal(int, int, object)

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
        #self.speed_timer.timeout.connect(self.send_speed_command)
        self.speed_timer.start(200)
        self.pix_rect = QRect(0, 0, 0, 0)
        self.setMouseTracking(True)
        self.press_pos = None
        self.current_pos = None

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
        self.pix_rect = QRect(int(x), int(y), int(w), int(h))
        painter.drawPixmap(self.pix_rect, self.pix, self.pix.rect())

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

        pos_cmd = self.getPosCmd()
        if pos_cmd is not None:
            x, y, theta = pos_cmd
            if theta is not None:
                painter.drawLine(self.press_pos.x(), self.press_pos.y(), self.current_pos.x(), self.current_pos.y())
                a1 = self.current_pos + QPoint(ARROW_SIZE * cos(-theta + ARROW_ANGLE),
                                               ARROW_SIZE * sin(-theta + ARROW_ANGLE))
                a2 = self.current_pos + QPoint(ARROW_SIZE * cos(-theta - ARROW_ANGLE),
                                               ARROW_SIZE * sin(-theta - ARROW_ANGLE))
                painter.setBrush(Qt.black)
                painter.drawPolygon(a1, self.current_pos, a2)

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
            self.speed_cmd.speed.vy = CMD_SPEED * mult
        elif e.key() == Qt.Key_D:
            self.speed_cmd.speed.vy = -CMD_SPEED * mult
        elif e.key() == Qt.Key_A:
            self.speed_cmd.speed.vtheta = CMD_OMEGA * mult
        elif e.key() == Qt.Key_E:
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
            self.speed_cmd.speed.vy = 0
        elif e.key() == Qt.Key_D:
            self.speed_cmd.speed.vy = 0
        elif e.key() == Qt.Key_A:
            self.speed_cmd.speed.vtheta = 0
        elif e.key() == Qt.Key_E:
            self.speed_cmd.speed.vtheta = 0
        elif e.key() == Qt.Key_Shift:
            self.speed_cmd.speed.vx /= 2
            self.speed_cmd.speed.vtheta /= 2
        self.send_speed_command()

    def send_speed_command(self):
        self.robot_manager.send_msg(self.robot_manager.current_rid, self.speed_cmd)

    def send_pos_cmd(self, x, y, theta=None):
        pos_cmd = m.Message()
        pos_cmd.pos.x = x
        pos_cmd.pos.y = y
        if theta is not None:
            pos_cmd.pos.theta = theta
        pos_cmd.msg_type = m.Message.COMMAND
        self.robot_manager.send_msg(self.robot_manager.current_rid, pos_cmd)

    def mapToTable(self, pos: QPoint):
        x = (pos.x() - self.pix_rect.left()) * 3000 / self.pix_rect.width()
        y = 2000 - ((pos.y() - self.pix_rect.top()) * 2000 / self.pix_rect.height())
        return round(x), round(y)

    def getPosCmd(self):
        if self.press_pos is not None and self.current_pos is not None:
            x, y = self.mapToTable(self.press_pos)
            dx = self.current_pos.x() - self.press_pos.x()
            dy = self.press_pos.y() - self.current_pos.y()  # y axis is inverted
            if abs(dx) > POS_ORIENT_THRESHOLD or abs(dy) > POS_ORIENT_THRESHOLD:
                theta = atan2(dy, dx)
            else:
                rpos = self.robot_manager.robots[self.robot_manager.current_rid].pos
                if rpos.HasField("pos"):
                    theta = rpos.pos.theta
                else:
                    theta = 0
            return x, y, theta

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        self.mouse_pos_changed.emit(*self.mapToTable(e.pos()))
        self.current_pos = e.pos()
        if self.press_pos is not None:
            self.update()
            x, y, theta = self.getPosCmd()
            self.pos_cmd_changed.emit(x, y, theta)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.setFocus()
        self.press_pos = e.pos()
        self.current_pos = e.pos()
        x, y, theta = self.getPosCmd()
        self.pos_cmd_changed.emit(x, y, theta)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if self.press_pos is not None:
            x, y, theta = self.getPosCmd()
            self.press_pos = None
            self.send_pos_cmd(x, y, theta)
            print(x, y, theta)
            self.pos_cmd_changed.emit(x, y, theta)
            self.update()

