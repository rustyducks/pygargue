from PyQt5 import QtCore, QtWidgets, QtGui, QtSvg
import time
import math
import sys
import robot


class TableView(QtWidgets.QGraphicsView):

    def __init__(self, *args, **kwargs):
        QtWidgets.QGraphicsView.__init__(self, *args, **kwargs)
        self._scene = QtWidgets.QGraphicsScene()#(0, 0, 3000, 2000, self)
        self.setScene(self._scene)
        pix = QtGui.QPixmap("map.png")
        pixitem = QtWidgets.QGraphicsPixmapItem(pix)
        # m = QtSvg.QGraphicsSvgItem("map.svg")
        # m.setScale(0.1)
        self._scene.addItem(pixitem)
        self.scale(0.3, 0.3)

        self.robots = []

        self.t = QtCore.QTimer()
        self.t.timeout.connect(lambda: print("plop"))
        self.t.start(500)

    def addRobot(self, r: robot.Robot):
        self.robots.append(r)
        r.pos_changed.connect(self.update_robot_pos)

    def update_robot_pos(self, pos: robot.Pos):
        print(pos)





class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        self.table_view = TableView(self._main)
        layout.addWidget(self.table_view)


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
