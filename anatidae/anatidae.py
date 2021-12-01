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
from radio_udp import RadioUDP
from logger import Logger
from PyQt5.QtNetwork import QUdpSocket, QHostAddress
from utils import UDPConnexion

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


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.robot_manager = RobotsManager()
        self.robot_tabs.set_robot_manager(self.robot_manager)
        self.table_view.set_robot_manager(self.robot_manager)
        self.table_view.setFocus()
        self.logger = Logger("/tmp/robot.log")
        #self.rsp= RadioSP("/dev/pts/5", 115200, self.logger, rid="Daneel", parent=self)

        self.rudps = []
        for c in cs:
            r = RadioUDP(c, self.logger, parent=self)
            self.robot_manager.add_radio(r)
            self.rudps.append(r)

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
