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

cs = [
        UDPConnexion("Dalek base", "127.0.0.1", 3456, "0.0.0.0", 3333, "Dalek", ["speed", "motor_pid"]),
        UDPConnexion("Dalek IO", "127.0.0.1", 3457, "0.0.0.0", 3334, "Dalek", ["arm", "hat", "procedure_cmd"]),
        #         connexion name,   dst,     dst port, src,  local port, associated rid, allowed
    ]
# dst is where the bridge is running (where the serial port is)
# dst port is the UDP port on wich the bridge is listening
# local_port is the port this radio will receive data
# associated rid : the rid associated with this connexion
# allowed : which messages can be sent to this connexion


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
        #self.rsp= RadioSP("/dev/pts/5", 115200, self.logger, rid="Daneel", parent=self)
        self.table_view.mouse_pos_changed.connect(self.update_mouse_pos)
        self.table_view.pos_cmd_changed.connect(self.update_pos_cmd)

        self.rudps = []
        for c in cs:
            r = RadioUDP(c, self.logger, parent=self)
            self.robot_manager.add_radio(r)
            self.rudps.append(r)

    def update_mouse_pos(self, x, y):
        self.pos_label.setText(f"X:{x:4} Y:{y:4}")

    def update_pos_cmd(self, x, y, theta):
        if theta is None:
            self.cmd_label.setText(f"cmd X:{x:4},Y:{y:4},None")
        else:
            self.cmd_label.setText(f"cmd X:{x:4},Y:{y:4},{theta:.2f}")

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.robot_manager.stop()
        for r in self.rudps:
            r.stop()
        self.logger.stop()
        super(MainWindow, self).closeEvent(e)


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = MainWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
