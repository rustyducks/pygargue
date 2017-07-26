from enum import Enum

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPolygonF

TABLE_WIDTH = 3000  # obstacles coordinates will usually be 0<= x <= TABLE_WIDTH
TABLE_HEIGHT = 2000  # obstacles coordinates will usually be 0 <= y < TABLE_HEIGHT


class ObstacleType(Enum):
    POLYGON = 0
    CIRCLE = 1


class Obstacle:
    def __init__(self, type):
        self.type = type

    def to_qobject(self, x_offset, y_offset, width, height):
        raise NotImplementedError("This is an Interface class")


class Polygon(Obstacle):
    def __init__(self):
        super().__init__(ObstacleType.POLYGON)
        self.points = [] # expected [(x0, y0), (x1, y1), ...]

    def to_qobject(self, x_offset, y_offset, width, height):
        width_factor = width / TABLE_WIDTH
        height_factor = height / TABLE_HEIGHT
        polygon = QPolygonF()
        for pt in self.points:
            polygon.append(QPointF(width - (pt[0] * width_factor + x_offset), pt[1] * height_factor + y_offset)) # X coordinates must be symetrical because the table and the window origin are not the same
        return "drawPolygon", polygon


class Circle(Obstacle):
    def __init__(self):
        super().__init__(ObstacleType.CIRCLE)
        self.center = None  # (xc, yc)
        self.radius = None

    def to_qobject(self, x_offset, y_offset, width, height):
        width_factor = width / TABLE_WIDTH
        height_factor = height / TABLE_HEIGHT
        rect_width = self.radius * 2 * width_factor
        rect_height = self.radius * 2 * height_factor
        top_left_x = width - (self.center[0] - self.radius) * width_factor + x_offset - rect_width # X coordinates must be symetrical because the table and the window origin are not the same
        top_left_y = (self.center[1] - self.radius) * height_factor + y_offset
        ellipse = QRectF(top_left_x, top_left_y, rect_width, rect_height)
        return "drawEllipse", ellipse



