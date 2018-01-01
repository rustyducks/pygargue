from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QWidget

from obstacle import TABLE_WIDTH, TABLE_HEIGHT


class Point:
    def __init__(self, ident, x, y):
        self.id = ident
        self.x = x
        self.y = y

    def get_qcolor(self):
        d = (0xff, 0xdd, 0xbb, 0x99, 0x77, 0x55)[(self.id // 6) % 6]
        r, v, b = ((d, 0, 0), (0, d, 0), (0, 0, d), (d, d, 0), (d, 0, d), (0, d, d))[self.id % 6]
        return QColor(r, v, b)

    def paint(self, painter, x_offset, y_offset, width, height):
        width_factor = width / TABLE_WIDTH
        height_factor = height / TABLE_HEIGHT
        painter.setBrush(QBrush(self.get_qcolor()))
        painter.setPen(QPen(self.get_qcolor()))
        painter.drawLine(QPointF(width - self.x * width_factor + x_offset - 10, self.y * height_factor + y_offset),
                         QPointF(width - self.x * width_factor + x_offset + 10, self.y * height_factor + y_offset))
        painter.drawLine(QPointF(width - self.x * width_factor + x_offset, self.y * height_factor + y_offset - 10),
                         QPointF(width - self.x * width_factor + x_offset, self.y * height_factor + y_offset + 10))

