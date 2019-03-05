import math
from PyQt5.QtCore import QRectF, QPointF, QLineF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import QWidget, QPushButton

from obstacle import TABLE_HEIGHT, TABLE_WIDTH

ROBOT_COLOR = (0,255,0, 180)
ROBOT_ORIENTATION_COLOR = (0,0,0)
ROBOT_TRAJECTORY_COLOR = (215,215,215)

class QRobot(QWidget):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.position = (1500, 1000)  # type:(int, int)
        self.orientation = 0  # radians type:float
        self.radius = 150
        self.trajectory = []  # type:list(tuple(int))

    def paint(self, painter, x_offset, y_offset, width, height):
        self._paint_trajectory(painter, x_offset, y_offset, width, height)
        old_brush = painter.brush()
        old_pen = painter.pen()
        width_factor = width / TABLE_WIDTH
        height_factor = height / TABLE_HEIGHT
        rect_width = self.radius * 2 * width_factor
        rect_height = self.radius * 2 * height_factor
        top_left_x = width - (self.position[0] - self.radius) * width_factor + x_offset - rect_width
        top_left_y = (self.position[1] - self.radius) * height_factor + y_offset
        painter.setPen(QPen(QColor(*ROBOT_COLOR)))
        painter.setBrush(QBrush(QColor(*ROBOT_COLOR)))
        painter.drawEllipse(QRectF(top_left_x, top_left_y, rect_width, rect_height))
        painter.setPen(QPen(QColor(*ROBOT_ORIENTATION_COLOR)))
        painter.setBrush(QBrush(QColor(*ROBOT_ORIENTATION_COLOR)))
        painter.drawLine(QPointF(width - self.position[0] * width_factor + x_offset,
                                 self.position[1] * height_factor + y_offset),
                         QPointF(width - (self.position[0] + math.cos(self.orientation) * self.radius) * width_factor + x_offset,
                                 (self.position[1] + math.sin(self.orientation) * self.radius) * height_factor + y_offset))

    def paint_angles(self, angles, painter, x_offset, y_offset, width, height):
        width_factor = width / TABLE_WIDTH
        height_factor = height / TABLE_HEIGHT
        for angle in angles.items():
            color = self.get_qcolor(angle[0])
            painter.setPen(QPen(color))
            painter.setBrush(QBrush(color))
            painter.drawLine(QPointF(width - self.position[0] * width_factor + x_offset,
                                 self.position[1] * height_factor + y_offset),
                         QPointF(width - (self.position[0] + math.cos(angle[1]) * self.radius) * width_factor + x_offset,
                                 (self.position[1] + math.sin(angle[1]) * self.radius) * height_factor + y_offset))


    def _paint_trajectory(self, painter, x_offset, y_offset, width, height):
        if self.trajectory is None or len(self.trajectory) == 0:
            return
        width_factor = width / TABLE_WIDTH
        height_factor = height / TABLE_HEIGHT
        painter.setPen(QPen(QColor(*ROBOT_TRAJECTORY_COLOR)))
        painter.setBrush(QBrush(QColor(*ROBOT_TRAJECTORY_COLOR)))
        q_trajectory = [QLineF(width - self.position[0] * width_factor + x_offset,
                                 self.position[1] * height_factor + y_offset,
                               width - self.trajectory[0][0] * width_factor + x_offset,
                               self.trajectory[0][1] * height_factor + y_offset)]

        for i in range(1, len(self.trajectory)):
            x1 = width - self.trajectory[i - 1][0] * width_factor + x_offset
            y1 = self.trajectory[i-1][1] * height_factor + y_offset
            x2 = width - self.trajectory[i][0] * width_factor + x_offset
            y2 = self.trajectory[i][1] * height_factor + y_offset
            q_trajectory.append(QLineF(x1, y1, x2, y2))


        painter.drawLines(q_trajectory)

    def get_qcolor(self, i):
        d = (0xff, 0xdd, 0xbb, 0x99, 0x77, 0x55)[(i // 6) % 6]
        r, v, b = ((d, d, 0), (d, 0, d), (0, d, d), (d, 0, 0), (0, d, 0), (0, 0, d))[i % 6]
        return QColor(r, v, b)
