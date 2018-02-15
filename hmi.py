from PyQt5 import QtCore, QtGui, QtWidgets
import ui


class Hmi(QtWidgets.QMainWindow):
    """Class to manage the main HMI behavior."""
    def __init__(self):
        super(Hmi, self).__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        
    def init_all_hmi(self):
        pass
