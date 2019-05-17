from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel, QPushButton
import sys


class Main(QWidget):


    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        layout  = QHBoxLayout(self)
        label = QLabel()
        label.setStyleSheet("QLabel { background-color : red; color : blue; }")
        layout.addWidget(label)
        layout.addWidget(QPushButton("new"))

    def mousePressEvent(self, QMouseEvent):
        #print mouse position
        print(QMouseEvent.pos())


a = QApplication([])
m = Main()
m.show()
sys.exit(a.exec_())