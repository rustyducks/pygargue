from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
from robot import *
import robots_manager
from messenger import Messenger
from utils import *
from math import cos, sin, pi

CMD_SPEED = 100
CMD_OMEGA = 0.3


ROBOT_SIZE = 30
ARROW_SIZE = 15
ARROW_ANGLE = pi + pi/8


class TableView(QWidget):

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.pix = QPixmap("data/map2022.png")
        self.robot_manager = None
        self.messenger = Messenger()
        self.speed_cmd = Speed(0, 0, 0)

    def set_robot_manager(self, rman):
        self.robot_manager = rman  # type: robots_manager.RobotsManager
        self.robot_manager.robot_pos_changed.connect(self.update)
        self.robot_manager.register_emiter(self.messenger)

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
            xr = r.pos.x * w / 3000 + x
            yr = (2000 - r.pos.y) * h / 2000 + y
            painter.setBrush(Qt.red)
            center = QPoint(int(xr), int(yr))
            painter.drawEllipse(center, ROBOT_SIZE, ROBOT_SIZE)
            head = center + QPoint(ROBOT_SIZE * cos(-r.pos.theta), ROBOT_SIZE * sin(-r.pos.theta))
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(center, head)
            a1 = head + QPoint(ARROW_SIZE*cos(-r.pos.theta + ARROW_ANGLE), ARROW_SIZE*sin(-r.pos.theta + ARROW_ANGLE))
            a2 = head + QPoint(ARROW_SIZE * cos(-r.pos.theta - ARROW_ANGLE), ARROW_SIZE * sin(-r.pos.theta - ARROW_ANGLE))
            painter.setBrush(Qt.black)
            painter.drawPolygon(a1, head, a2)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.isAutoRepeat():
            return
        mult = 1
        if e.modifiers() & Qt.ShiftModifier:
            mult = 2
        if e.key() == Qt.Key_Z:
            self.speed_cmd.vx = CMD_SPEED * mult
        elif e.key() == Qt.Key_S:
            self.speed_cmd.vx = -CMD_SPEED * mult
        elif e.key() == Qt.Key_Q:
            self.speed_cmd.vtheta = CMD_OMEGA * mult
        elif e.key() == Qt.Key_D:
            self.speed_cmd.vtheta = -CMD_OMEGA * mult
        elif e.key() == Qt.Key_Shift:
            self.speed_cmd.vx *= 2
            self.speed_cmd.vtheta *= 2
        self.messenger.set_speed_cmd(self.speed_cmd)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if e.isAutoRepeat():
            return
        if e.key() == Qt.Key_Z:
            self.speed_cmd.vx = 0
        elif e.key() == Qt.Key_S:
            self.speed_cmd.vx = 0
        elif e.key() == Qt.Key_Q:
            self.speed_cmd.vtheta = 0
        elif e.key() == Qt.Key_D:
            self.speed_cmd.vtheta = 0
        elif e.key() == Qt.Key_Shift:
            self.speed_cmd.vx /= 2
            self.speed_cmd.vtheta /= 2
        self.messenger.set_speed_cmd(self.speed_cmd)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.setFocus()
        pass

