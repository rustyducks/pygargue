import math
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import QWidget, QPushButton

from obstacle import TABLE_HEIGHT, TABLE_WIDTH

ROBOT_COLOR = (0,255,0)
ROBOT_ORIENTATION_COLOR = (0,0,0)

class QRobot(QWidget):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.position = (200, 1800)  # type:(int, int)
        self.orientation = 0  # radians type:float
        self.radius = 150

    def paint(self, painter, x_offset, y_offset, width, height):
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
