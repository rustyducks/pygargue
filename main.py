import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QPen, QColor, QBrush, QPolygonF, QPainter, QImage
from PyQt5.QtCore import QPointF
 
class App(QImage):
 
    def __init__(self):
        super().__init__(3000, 2000, QImage.Format_RGB32)
        self.fill(0xffffffff)
        self.left = 10
        self.top = 10
        self.width = 3000
        self.height = 2000
        self.initUI()
 
    def initUI(self):
        #self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
         
        
        self.pen = QPen(QColor(0,0,0))
        self.pen.setWidth(1)
        self.brush = QBrush(QColor(0,0,0))
        self.polygon = QPolygonF()
        self.polygon.append(QPointF(250, 800))
        self.polygon.append(QPointF(250,200))
        self.polygon.append(QPointF(750, 200))
        self.polygon.append(QPointF(750, 800))

        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
        #self.show()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    #label = QLabel()
    #label.setPixmap(QPixmap.fromImage(ex));
    #label.show();
    print(QColor(ex.pixel(500, 250)).getRgb())
    #sys.exit(app.exec_())
