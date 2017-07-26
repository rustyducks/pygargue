import timeit

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QImage, QPen, QColor, QBrush, QPolygonF, QPainter
import numpy as np

COLOR_FREE = 0xffffffff  # 0xAARRGGBB
COLOR_OBSTACLE = 0xff000000  # 0xAARRGGBB

class ObstacleMap(QImage):
    def __init__(self):
        super().__init__(3000, 2000, QImage.Format_RGB32)
        self.fill(COLOR_FREE)
        self.left = 10
        self.top = 10
        self.width = 3000
        self.height = 2000
        self.pen = QPen(QColor(COLOR_OBSTACLE))
        self.pen.setWidth(1)
        self.brush = QBrush(QColor(0, 0, 0))
        self.polygon = QPolygonF()
        self.polygon.append(QPointF(250, 800))
        self.polygon.append(QPointF(250, 200))
        self.polygon.append(QPointF(750, 200))
        self.polygon.append(QPointF(750, 800))
        self.init_ui()

    def init_ui(self):
        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)

    def generate_obstacle_grid(self):
        start = timeit.default_timer()
        array = np.zeros((self.width, self.height))
        for i in range(self.height):
            for j in range(self.width):
                if QColor(self.pixel(j, i)) == QColor(COLOR_OBSTACLE):
                    array[j,i] = 1
        stop = timeit.default_timer()
        print(stop - start)
        return array


    def dump_obstacle_grid_to_file(self, filename):
        np.savetxt(filename, self.generate_obstacle_grid())