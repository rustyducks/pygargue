import timeit

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QImage, QPen, QColor, QBrush, QPolygonF, QPainter
import numpy as np

COLOR_FREE = 0xffffffff  # 0xAARRGGBB
COLOR_OBSTACLE = 0xff000000  # 0xAARRGGBB

class ObstacleMap(QImage):
    def __init__(self, obstacles, ratio):
        super().__init__(int(3000 * ratio), int(2000 * ratio), QImage.Format_RGB32)
        self.fill(COLOR_FREE)
        self.left = 10
        self.top = 10
        self.table_width = int(3000 * ratio)
        self.table_height = int(2000 * ratio)
        self.pen = QPen(QColor(COLOR_OBSTACLE))
        self.pen.setWidth(1)
        self.brush = QBrush(QColor(0, 0, 0))
        self.obstacles = obstacles
        self.init_ui()

    def init_ui(self):
        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        for obs in self.obstacles:
            draw_function_name, draw_object = obs.to_qobject(0, 0, self.table_width - 1, self.table_height - 1)
            paint_function = getattr(painter, draw_function_name)  # get the method of painter
            paint_function(draw_object)

    def generate_obstacle_grid(self):
        start = timeit.default_timer()
        array = np.zeros((self.table_width, self.table_height))
        for i in range(self.table_height):
            for j in range(self.table_width):
                if QColor(self.pixel(j, i)) == QColor(COLOR_OBSTACLE):
                    array[self.table_width - 1 -j,i] = 1
        stop = timeit.default_timer()
        print(stop - start)
        return array


    def dump_obstacle_grid_to_file(self, filename):
        array = self.generate_obstacle_grid()
        with open(filename, 'w') as f:
            for i in range(self.table_height):
                for j in range(self.table_width):
                    f.write(str(array[j, i])[0])
                f.write('\n')
            f.close()
