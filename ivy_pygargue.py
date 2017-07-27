import ivy
from ivy.std_api import *

from obstacle import Polygon, Circle

IVY_APP_NAME = "Pygargue"
DEFAULT_BUS = '127.255.255.255:2010'

NEW_POLYGON_OBSTACLE_REGEXP = "New Obstacle id : (.*) type : POLYGON points : (.*)"  # eg : New Obstacle id : 3 type : POLYGON points : 1500,350;1500,650;1000,650;1000,350
NEW_CIRCLE_OBSTACLE_REGEXP = "New Obstacle id : (.*) type : CIRCLE center : (.*) radius : (.*)"  # eg : New Obstacle id : 6 type : CIRCLE center : 500,800 radius : 150
ROBOT_POSITION_REGEXP = "Robot position (.*) orientation (.*)"  # eg : Robot position 552,789 orientation 3.14159265
NEW_TRAJECTORY_REGEXP = "New trajectory (.*)"  # eg : New trajectory 528,450;1200,564;846,1486

class Ivy:
    def __init__(self, application, bus=DEFAULT_BUS):
        self.app = application
        IvyInit(IVY_APP_NAME, IVY_APP_NAME + "online", 0, lambda agent, event: None, lambda agent, event: None)
        IvyStart(bus)
        IvyBindMsg(self.on_new_polygon_obstacle, NEW_POLYGON_OBSTACLE_REGEXP)
        IvyBindMsg(self.on_new_circle_obstacle, NEW_CIRCLE_OBSTACLE_REGEXP)
        IvyBindMsg(self.on_new_robot_position, ROBOT_POSITION_REGEXP)
        IvyBindMsg(self.on_new_trajectory, NEW_TRAJECTORY_REGEXP)

    def on_new_polygon_obstacle(self, agent, *arg):
        polygon = Polygon()
        for pt in arg[1].split(";"):
            x, y = pt.split(',')
            polygon.points.append((float(x), float(y)))
        self.app.obstacles.append(polygon)
        self.app.repaint()

    def on_new_circle_obstacle(self, agent, *arg):
        circle = Circle()
        xc, yc = arg[1].split(',')
        circle.center = (float(xc), float(yc))
        circle.radius = float(arg[2])
        self.app.obstacles.append(circle)
        self.app.repaint()

    def on_new_robot_position(self, agent, *arg):
        x, y = arg[0].split(',')
        self.app.move_robot(float(x), float(y), float(arg[1]))

    def on_new_trajectory(self, agent, *arg):
        trajectory = []
        for pt in arg[0].split(';'):
            x, y = pt.split(',')
            trajectory.append((int(x),int(y)))
        self.app.new_trajectory(trajectory)


    def stop(self):
        IvyStop()
