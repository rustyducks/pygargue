from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow
import time
import math
import sys
import robot
from typing import List
from robots_manager import RobotsManager
from table_view import TableView
from robot_status import RobotStatus
from generated.window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.robot_manager = RobotsManager()
        self.robot_status.set_robot_manager(self.robot_manager)
        self.table_view.set_robot_manager(self.robot_manager)
        self.table_view.setFocus()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.resize(1000, 600)
        self.setCentralWidget(self._main)
        layout = QtWidgets.QHBoxLayout(self._main)
        self.robot_manager = RobotsManager()
        self.table_view = TableView(self.robot_manager, self._main)
        self.status_view = RobotStatus(self.robot_manager, self._main)
        self.table_view.setFocus()
        layout.addWidget(self.table_view)
        layout.addWidget(self.status_view)

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.robot_manager.stop()
        super(ApplicationWindow, self).closeEvent(e)


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    #app = ApplicationWindow()
    app = MainWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
