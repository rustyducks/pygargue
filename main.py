import PyQt5.QtWidgets as Widgets
import sys
import hmi
import signal

def main():
    app = Widgets.QApplication(sys.argv)

    main_window = hmi.Hmi()
    main_window.init_all_hmi()
    main_window.show()
    
    app.aboutToQuit.connect(main_window.ui.mapWidget.on_quit)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
