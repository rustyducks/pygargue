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
GRAPH_TABLE_RATIO = 0.1  # graph/table ratio for discreted graph generation

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
        self.obstacles = {}  # type:dict[int: Obstacle]
        self.highlighted_point = {}  # type: dict[int: Point]
        self.highlighted_angles = {}  # type: dict[int, float]
        self.feed_forward_arrow = None  # ((xs, ys), (xe, ye))
        self.feed_forward_arrow_enabled = False
        self.robot_speed_command = [0, 0, 0]
        self.repaint_mutex = Lock()
        self.ivy = Ivy(self)
        self.repaint_mutex.acquire()
        self.initUI()
        self.repaint_mutex.release()
        self.running = False
 
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
        for obs in self.obstacles.values():
            painter.setPen(QPen(QColor(*OBSTACLE_COLOR)))
            painter.setBrush(QBrush(QColor(*OBSTACLE_COLOR)))
            draw_function_name, draw_object = obs.to_qobject(0, 0, self.table_width - 1, self.table_height - 1)
            paint_function = getattr(painter, draw_function_name)  # get the method of painter
            paint_function(draw_object)
            painter.setPen(QPen(QColor(*OBSTACLE_COLOR, 150)))
            painter.setBrush(QBrush(QColor(*OBSTACLE_COLOR, 150)))
            draw_function_name, draw_object = obs.to_qobject(0, 0, self.table_width - 1, self.table_height - 1,
                                                             inflate_radius=self.robot.radius)
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
        left_red_zone = QPolygonF()
        left_red_zone.append(QPointF(0 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        left_red_zone.append(QPointF(0 * width_factor + x_offset, height - (1700 * height_factor + y_offset)))
        left_red_zone.append(QPointF(450 * width_factor + x_offset, height - (1700 * height_factor + y_offset)))
        left_red_zone.append(QPointF(450 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        painter.setPen(QPen(QColor(217, 25, 32)))
        painter.setBrush(QBrush(QColor(217, 25, 32)))
        painter.drawPolygon(left_red_zone)
        left_green_zone = QPolygonF()
        left_green_zone.append(QPointF(0 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        left_green_zone.append(QPointF(0 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        left_green_zone.append(QPointF(450 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        left_green_zone.append(QPointF(450 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        painter.setPen(QPen(QColor(76, 190, 75)))
        painter.setBrush(QBrush(QColor(76, 190, 75)))
        painter.drawPolygon(left_green_zone)
        left_blue_zone = QPolygonF()
        left_blue_zone.append(QPointF(0 * width_factor + x_offset, height - (800 * height_factor + y_offset)))
        left_blue_zone.append(QPointF(0 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        left_blue_zone.append(QPointF(450 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        left_blue_zone.append(QPointF(450 * width_factor + x_offset, height - (800 * height_factor + y_offset)))
        painter.setPen(QPen(QColor(41, 126, 203)))
        painter.setBrush(QBrush(QColor(41, 126, 203)))
        painter.drawPolygon(left_blue_zone)
        right_red_zone = QPolygonF()
        right_red_zone.append(QPointF(2550 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        right_red_zone.append(QPointF(2550 * width_factor + x_offset, height - (1700 * height_factor + y_offset)))
        right_red_zone.append(QPointF(3000 * width_factor + x_offset, height - (1700 * height_factor + y_offset)))
        right_red_zone.append(QPointF(3000 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        painter.setPen(QPen(QColor(217, 25, 32)))
        painter.setBrush(QBrush(QColor(217, 25, 32)))
        painter.drawPolygon(right_red_zone)
        right_green_zone = QPolygonF()
        right_green_zone.append(QPointF(2550 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        right_green_zone.append(QPointF(2550 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        right_green_zone.append(QPointF(3000 * width_factor + x_offset, height - (1400 * height_factor + y_offset)))
        right_green_zone.append(QPointF(3000 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        painter.setPen(QPen(QColor(76, 190, 75)))
        painter.setBrush(QBrush(QColor(76, 190, 75)))
        painter.drawPolygon(right_green_zone)
        right_blue_zone = QPolygonF()
        right_blue_zone.append(QPointF(2550 * width_factor + x_offset, height - (800 * height_factor + y_offset)))
        right_blue_zone.append(QPointF(2550 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        right_blue_zone.append(QPointF(3000 * width_factor + x_offset, height - (1100 * height_factor + y_offset)))
        right_blue_zone.append(QPointF(3000 * width_factor + x_offset, height - (800 * height_factor + y_offset)))
        painter.setPen(QPen(QColor(41, 126, 203)))
        painter.setBrush(QBrush(QColor(41, 126, 203)))
        painter.drawPolygon(right_blue_zone)

        left_chaos_zone = QRectF(850 * width_factor + x_offset, height - 1100 * height_factor + y_offset,
                                 300 * width_factor, 300 * height_factor)
        right_chaos_zone = QRectF(1850 * width_factor + x_offset, height - 1100 * height_factor + y_offset,
                                  300 * width_factor, 300 * height_factor)
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.setBrush(QBrush(QColor(0, 0, 0, 75)))
        painter.drawEllipse(left_chaos_zone)
        painter.drawEllipse(right_chaos_zone)

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
        if event.isAutoRepeat():
            return
        key = event.key()
        if key == Qt.Key_G:
            img = ObstacleMap(self.obstacles.values(), GRAPH_TABLE_RATIO, self.robot.radius)
            print("dumping")
            img.dump_obstacle_grid_to_file("graph.pbm")
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
        elif key == Qt.Key_Agrave:
            self.ivy.send_action(10)
        elif key == Qt.Key_ParenRight:
            self.ivy.send_action(11)
        elif key == Qt.Key_Equal:
            self.ivy.send_action(12)
        elif key == Qt.Key_Z:
            self.robot_speed_command[0] = 1
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_S:
            self.robot_speed_command[0] = -1
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_Q:
            self.robot_speed_command[2] = 1
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_D:
            self.robot_speed_command[2] = -1
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_Shift:
            self.running = True
            self.send_speed_direction(self.robot_speed_command)

    def send_speed_direction(self, cmds):
        mod_cmds = cmds
        if self.running is True:
            mod_cmds = list(map(lambda n:n*2, cmds))
        self.ivy.send_speed_direction(mod_cmds)


    def keyReleaseEvent(self, event:QKeyEvent):
        if event.isAutoRepeat():
            return
        key = event.key()
        if key == Qt.Key_Z:
            self.robot_speed_command[0] = 0
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_S:
            self.robot_speed_command[0] = 0
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_Q:
            self.robot_speed_command[2] = 0
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_D:
            self.robot_speed_command[2] = 0
            self.send_speed_direction(self.robot_speed_command)
        elif key == Qt.Key_Shift:
            self.running = False
            self.send_speed_direction(self.robot_speed_command)

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
            self.ivy.send_go_to(int(self.x_press), 2000 - int(self.y_press))
        else:
            width_factor = self.table_width / 3000
            height_factor = self.table_height / 2000
            x_release = event.x() / width_factor
            y_release = event.y() / height_factor
            dx = x_release - self.x_press
            dy = y_release - self.y_press
            theta = atan2(-dy, dx)
            self.ivy.send_go_to_orient(int(self.x_press), 2000 - int(self.y_press), theta)
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
