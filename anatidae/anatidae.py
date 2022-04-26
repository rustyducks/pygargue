#!/usr/bin/python3
import PyQt5.QtGui
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QFontDatabase
import sys
from robots_manager import RobotsManager
from radio_sp import RadioSP
from radio_udp import RadioUDP
from logger import Logger
from utils import UDPConnexion
from robot_tabs import RobotTabs
from table_view import TableView
import json
from serial.serialutil import SerialException


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Anatidae")
        self.resize(739, 481)
        self.splitter = QtWidgets.QSplitter()
        self.table_view = TableView(self.splitter)
        self.robot_tabs = RobotTabs(self.splitter)
        self.splitter.setStretchFactor(0, 1)
        self.setCentralWidget(self.splitter)
        self.robot_tabs.setCurrentIndex(-1)


        # self.menubar = QtWidgets.QMenuBar(self)
        # self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.pos_label = QtWidgets.QLabel()
        self.cmd_label = QtWidgets.QLabel()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.pos_label.setFont(font)
        self.cmd_label.setFont(font)
        self.statusbar.addPermanentWidget(self.cmd_label, 1)
        self.statusbar.addPermanentWidget(self.pos_label)

        self.robot_manager = RobotsManager()
        self.robot_tabs.set_robot_manager(self.robot_manager)
        self.table_view.set_robot_manager(self.robot_manager)
        self.table_view.setFocus()
        self.logger = Logger("/tmp/robot.log")
        self.table_view.mouse_pos_changed.connect(self.update_mouse_pos)
        self.table_view.pos_cmd_changed.connect(self.update_pos_cmd)
        self.radios_from_file("radios.json")
        

    def update_mouse_pos(self, x, y):
        self.pos_label.setText(f"X:{x:4} Y:{y:4}")

    def update_pos_cmd(self, x, y, theta):
        if theta is None:
            self.cmd_label.setText(f"cmd X:{x:4},Y:{y:4},None")
        else:
            self.cmd_label.setText(f"cmd X:{x:4},Y:{y:4},{theta:.2f}")

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.robot_manager.stop()
        self.logger.stop()
        super(MainWindow, self).closeEvent(e)

    def radios_from_file(self, filename):
            with open(filename, 'r') as fic:
                rjs = json.load(fic)
                for rj in rjs:
                    if rj["type"] == "UDP":
                        c = UDPConnexion(rj["name"], rj["addr"], rj["port"], rj["local_addr"], rj["local_port"], rj["rid"], rj["allowed"])
                        r = RadioUDP(c, self.logger, parent=self)
                        self.robot_manager.add_radio(r)
                    elif rj["type"] == "serial":
                        try:
                            r = RadioSP(rj["port"], rj["baudrate"], self.logger, rj["rid"], parent=self)
                            self.robot_manager.add_radio(r)
                        except SerialException as e:
                            print(e)
                    else:
                        print("Radio type {} unknown!".format(rj["type"]))


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = MainWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
