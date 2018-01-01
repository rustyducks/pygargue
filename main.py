import argparse
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QPen, QColor, QBrush, QPolygonF, QPainter, QImage, QPalette, QKeyEvent, \
    QMouseEvent
from PyQt5.QtCore import QPointF, pyqtSlot, QSize, QRectF

from ivy_pygargue import Ivy
from obstacle import Obstacle
from obstacle_map import ObstacleMap

import timeit

from q_robot import QRobot
from point import Point

OBSTACLE_COLOR = (66, 134, 244)
BACKGROUND_COLOR = (25, 25, 25)
GRAPH_TABLE_RATIO = 0.2  # graph/table ratio for discreted graph generation


class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = "Pygargue"
        self.table_left = 0
        self.table_top = 0
        self.table_width = 1200
        self.table_height = 800
        self.obstacles = []  # type:list[Obstacle]
        self.highlighted_point = {}  # type: dict[int, Point]
        self.ivy = Ivy(self)
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.table_left, self.table_top, self.table_width, self.table_height)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(*BACKGROUND_COLOR))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.pen = QPen(QColor(255,0,0))
        self.pen.setWidth(1)
        self.brush = QBrush(QColor(0,0,0))
        self.robot = QRobot(self)
        # painter = QPainter(self)
        # painter.setPen(self.pen)
        # painter.setBrush(self.brush)
        # painter.drawPolygon(self.polygon)
        self.show()

    def paintEvent(self, event):
        self.table_width = min(self.geometry().width(), self.geometry().height() * 3/2)
        # The table will keep the 3/2 ratio whatever the window ratio
        self.table_height = min(self.geometry().height(), self.geometry().width() * 2/3)
        painter = QPainter(self)
        self.paint_background(painter, 0, 0, self.table_width - 1, self.table_height - 1)
        painter.setPen(QPen(QColor(255,0,0)))
        painter.drawLine(0, 0, 0, self.table_height-1)
        painter.drawLine(0, self.table_height-1, self.table_width-1, self.table_height-1)
        painter.drawLine(self.table_width-1, self.table_height-1, self.table_width-1, 0)
        painter.drawLine(self.table_width-1, 0, 0, 0)
        painter.setPen(QPen(QColor(*OBSTACLE_COLOR)))
        painter.setBrush(QBrush(QColor(*OBSTACLE_COLOR)))
        for obs in self.obstacles:
            draw_function_name, draw_object = obs.to_qobject(0, 0, self.table_width - 1, self.table_height - 1)
            paint_function = getattr(painter, draw_function_name)  # get the method of painter
            paint_function(draw_object)
        for pt in self.highlighted_point.values():
            pt.paint(painter, 0, 0, self.table_width - 1, self.table_height - 1)

        self.robot.paint(painter, 0, 0, self.table_width - 1, self.table_height - 1)


    @pyqtSlot()
    def on_quit(self):
        self.ivy.stop()

    def paint_background(self, painter, x_offset, y_offset, width, height):
        old_brush = painter.brush()
        old_pen = painter.pen()
        width_factor = width / 3000
        height_factor = height / 2000
        start_yellow_zone = QPolygonF()
        start_yellow_zone.append(QPointF(width - (3000 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_yellow_zone.append(QPointF(width - (1930 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_yellow_zone.append(QPointF(width - (1930 * width_factor + x_offset), 1640 * height_factor + y_offset))
        start_yellow_zone.append(QPointF(width - (3000 * width_factor + x_offset), 1640 * height_factor + y_offset))
        painter.setPen(QPen(QColor(255, 255, 0)))
        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.drawPolygon(start_yellow_zone)
        start_blue_zone = QPolygonF()
        start_blue_zone.append(QPointF(width - (0 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_blue_zone.append(QPointF(width - (1070 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_blue_zone.append(QPointF(width - (1070 * width_factor + x_offset), 1640 * height_factor + y_offset))
        start_blue_zone.append(QPointF(width - (0 * width_factor + x_offset), 1640 * height_factor + y_offset))
        painter.setPen(QPen(QColor(0, 0, 255)))
        painter.setBrush(QBrush(QColor(0, 0, 255)))
        painter.drawPolygon(start_blue_zone)
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def move_robot(self, x, y, theta):
        self.robot.position = (x, y)
        self.robot.orientation = theta
        self.repaint()

    def new_trajectory(self, trajectory):
        self.robot.trajectory = trajectory
        self.repaint()

    def keyPressEvent(self, event:QKeyEvent):
        img = ObstacleMap(self.obstacles, GRAPH_TABLE_RATIO)
        print("dumping")
        img.dump_obstacle_grid_to_file("graph.txt")

    def mousePressEvent(self, event:QMouseEvent):
        width_factor = self.table_width / 3000
        height_factor = self.table_height / 2000
        x_click = event.x() / width_factor
        y_click = event.y() / height_factor
        self.ivy.send_go_to(3000 - int(x_click), int(y_click))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    #start = timeit.default_timer()
    ex = App()
    app.aboutToQuit.connect(ex.on_quit)
    #label = QLabel()
    #label.setPixmap(QPixmap.fromImage(ex))
    #label.show()
    #ex.dump_obstacle_grid_to_file("test.txt")
    #stop = timeit.default_timer()
    #print (stop - start)
    sys.exit(app.exec_())
