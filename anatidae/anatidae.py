from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow
import time
import math
import sys
from typing import List
from robots_manager import RobotsManager
from table_view import TableView
from robot_status import RobotStatus
from generated.window import Ui_MainWindow
from radio_sp import RadioSP
from logger import Logger


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.robot_manager = RobotsManager()
        self.robot_tabs.set_robot_manager(self.robot_manager)
        self.table_view.set_robot_manager(self.robot_manager)
        self.table_view.setFocus()
        self.logger = Logger("/tmp/robot.log")
        self.rsp = RadioSP("/dev/bmp_tty", 57600, self.logger, rid="Daneel", parent=self)
        self.robot_manager.add_radio(self.rsp)

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.robot_manager.stop()
        self.rsp.stop()
        self.logger.stop()
        super(MainWindow, self).closeEvent(e)


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = MainWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
