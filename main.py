import cv2
import time
import numpy as np 
import window
import label_yolo

class Application(object):
    def __init__(self):
        self.window = window.MyWidget()
        self.window = title('Label for yolo')