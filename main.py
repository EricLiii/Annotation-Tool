import cv2
import time
import sys
import numpy as np 
import window
import label_yolo
import window
from PySide2.QtWidgets import QApplication

class Application(object):
    def __init__(self):
        self.window = window.MyWidget('window/mainwindow.ui')
        self.label_tool = label_yolo.DatasetVerifier()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Application()
    

    sys.exit(app.exec_())