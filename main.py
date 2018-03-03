#!/usr/bin/python3

import argparse
import sys
from math import atan2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QPen, QColor, QBrush, QPolygonF, QPainter, QImage, QPalette, QKeyEvent, \
    QMouseEvent
from PyQt5.QtCore import QPointF, pyqtSlot, QSize, QRectF, Qt

from ivy_pygargue import Ivy
from obstacle import Obstacle
from obstacle_map import ObstacleMap
import math
import signal
from multiprocessing import Lock
import timeit

from q_robot import QRobot
from point import Point

OBSTACLE_COLOR = (66, 134, 244)
BACKGROUND_COLOR = (25, 25, 25)
FEEDFORWARD_ARROW_COLOR = (143, 183, 247)
GRAPH_TABLE_RATIO = 0.2  # graph/table ratio for discreted graph generation

THRESHOLD_DISTANCE_ANGLE_SELECTION = 20


class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = "Pygargue"
        self.table_left = 0
        self.table_top = 0
        self.table_width = 1200
        self.table_height = 800
        self.x_press = None
        self.y_press = None
        self.obstacles = []  # type:list[Obstacle]
        self.highlighted_point = {}  # type: dict[int, Point]
        self.highlighted_angles = {}  # type: dict[int, float]
        self.feed_forward_arrow = None  # ((xs, ys), (xe, ye))
        self.feed_forward_arrow_enabled = False
        self.repaint_mutex = Lock()
        self.ivy = Ivy(self)
        self.repaint_mutex.acquire()
        self.initUI()
        self.repaint_mutex.release()
 
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
        self.robot.paint_angles(self.highlighted_angles, painter, 0, 0, self.table_width - 1, self.table_height - 1)
        self.paint_feedforward(painter)


    @pyqtSlot()
    def on_quit(self):
        self.ivy.stop()

    def paint_background(self, painter, x_offset, y_offset, width, height):
        old_brush = painter.brush()
        old_pen = painter.pen()
        width_factor = width / 3000
        height_factor = height / 2000
        start_green_zone = QPolygonF()
        start_green_zone.append(QPointF(width - (0 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_green_zone.append(QPointF(width - (0 * width_factor + x_offset), 1350 * height_factor + y_offset))
        start_green_zone.append(QPointF(width - (400 * width_factor + x_offset), 1350 * height_factor + y_offset))
        start_green_zone.append(QPointF(width - (400 * width_factor + x_offset), 2000 * height_factor + y_offset))
        painter.setPen(QPen(QColor(97, 153, 59)))
        painter.setBrush(QBrush(QColor(97, 153, 59)))
        painter.drawPolygon(start_green_zone)
        start_orange_zone = QPolygonF()
        start_orange_zone.append(QPointF(width - (2600 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_orange_zone.append(QPointF(width - (3000 * width_factor + x_offset), 2000 * height_factor + y_offset))
        start_orange_zone.append(QPointF(width - (3000 * width_factor + x_offset), 1350 * height_factor + y_offset))
        start_orange_zone.append(QPointF(width - (2600 * width_factor + x_offset), 1350 * height_factor + y_offset))
        painter.setPen(QPen(QColor(208, 93, 40)))
        painter.setBrush(QBrush(QColor(208, 93, 40)))
        painter.drawPolygon(start_orange_zone)

        construction_zone_green = QPolygonF()
        construction_zone_green.append(QPointF(width - (400 * width_factor + x_offset), 1820 * height_factor + y_offset))
        construction_zone_green.append(QPointF(width - (400 * width_factor + x_offset), 2000 * height_factor + y_offset))
        construction_zone_green.append(QPointF(width - (960 * width_factor + x_offset), 2000 * height_factor + y_offset))
        construction_zone_green.append(QPointF(width - (960 * width_factor + x_offset), 1820 * height_factor + y_offset))
        painter.setPen(QPen(QColor(97, 153, 59)))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawPolygon(construction_zone_green)
        construction_zone_orange = QPolygonF()
        construction_zone_orange.append(QPointF(width - (2040 * width_factor + x_offset), 1820 * height_factor + y_offset))
        construction_zone_orange.append(QPointF(width - (2040 * width_factor + x_offset), 2000 * height_factor + y_offset))
        construction_zone_orange.append(QPointF(width - (2600 * width_factor + x_offset), 2000 * height_factor + y_offset))
        construction_zone_orange.append(QPointF(width - (2600 * width_factor + x_offset), 1820 * height_factor + y_offset))
        painter.setPen(QPen(QColor(208, 93, 40)))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawPolygon(construction_zone_orange)

        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def paint_feedforward(self, painter):
        if self.feed_forward_arrow is not None and self.feed_forward_arrow_enabled:
            painter.setPen(QPen(QColor(*FEEDFORWARD_ARROW_COLOR)))
            painter.setBrush(QBrush(QColor(*FEEDFORWARD_ARROW_COLOR)))
            painter.drawLine(QPointF(*self.feed_forward_arrow[0]), QPointF(*self.feed_forward_arrow[1]))
            angle = math.atan2(self.feed_forward_arrow[1][1] - self.feed_forward_arrow[0][1],
                               self.feed_forward_arrow[1][0] - self.feed_forward_arrow[0][0])
            painter.drawLine(QPointF(*self.feed_forward_arrow[1]), QPointF(
                self.feed_forward_arrow[1][0] + 10 * math.cos(angle + math.radians(150)),
                self.feed_forward_arrow[1][1] + 10 * math.sin(angle + math.radians(150))))
            painter.drawLine(QPointF(*self.feed_forward_arrow[1]), QPointF(
                self.feed_forward_arrow[1][0] + 10 * math.cos(angle - math.radians(150)),
                self.feed_forward_arrow[1][1] + 10 * math.sin(angle - math.radians(150))))

    def move_robot(self, x, y, theta):
        self.robot.position = (x, y)
        self.robot.orientation = theta
        self.repaint_mutex.acquire()
        self.repaint()
        self.repaint_mutex.release()

    def new_trajectory(self, trajectory):
        self.robot.trajectory = trajectory
        self.repaint_mutex.acquire()
        self.repaint()
        self.repaint_mutex.release()

    def keyPressEvent(self, event:QKeyEvent):
        key = event.key()
        if key == Qt.Key_D:
            img = ObstacleMap(self.obstacles, GRAPH_TABLE_RATIO)
            print("dumping")
            img.dump_obstacle_grid_to_file("graph.txt")
        elif key == Qt.Key_Ampersand:
            self.ivy.send_action(1)
        elif key == Qt.Key_Eacute:
            self.ivy.send_action(2)
        elif key == Qt.Key_QuoteDbl:
            self.ivy.send_action(3)
        elif key == Qt.Key_Apostrophe:
            self.ivy.send_action(4)
        elif key == Qt.Key_ParenLeft:
            self.ivy.send_action(5)
        elif key == Qt.Key_Minus:
            self.ivy.send_action(6)
        elif key == Qt.Key_Egrave:
            self.ivy.send_action(7)
        elif key == Qt.Key_Underscore:
            self.ivy.send_action(8)
        elif key == Qt.Key_Ccedilla:
            self.ivy.send_action(9)

    def mousePressEvent(self, event:QMouseEvent):
        width_factor = self.table_width / 3000
        height_factor = self.table_height / 2000
        self.x_press = event.x() / width_factor
        self.y_press = event.y() / height_factor
        self.feed_forward_arrow = ((event.x(), event.y()), (0, 0))

    def mouseMoveEvent(self, event:QMouseEvent):
        if self.feed_forward_arrow is not None and math.hypot(event.x() - self.feed_forward_arrow[0][0],
                                                              event.y() - self.feed_forward_arrow[0][1]) >= THRESHOLD_DISTANCE_ANGLE_SELECTION:
            self.feed_forward_arrow = (self.feed_forward_arrow[0], (event.x(), event.y()))
            self.feed_forward_arrow_enabled = True
            self.repaint_mutex.acquire()
            self.repaint()
            self.repaint_mutex.release()

    def mouseReleaseEvent(self, event:QMouseEvent):
        if math.hypot(event.x() - self.feed_forward_arrow[0][0], event.y() - self.feed_forward_arrow[0][1]) < THRESHOLD_DISTANCE_ANGLE_SELECTION:
            self.ivy.send_go_to(3000 - int(self.x_press), int(self.y_press))
        else:
            width_factor = self.table_width / 3000
            height_factor = self.table_height / 2000
            x_release = event.x() / width_factor
            y_release = event.y() / height_factor
            dx = x_release - self.x_press
            dy = y_release - self.y_press
            theta = atan2(dy, -dx)
            self.ivy.send_go_to_orient(3000 - int(self.x_press), int(self.y_press), theta)
        self.x_press = None
        self.y_press = None
        self.feed_forward_arrow = None
        self.feed_forward_arrow_enabled = False
        self.repaint_mutex.acquire()
        self.repaint()
        self.repaint_mutex.release()



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
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
