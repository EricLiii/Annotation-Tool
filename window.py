import os
import cv2
import time
import sys
import random
import shutil
import numpy as np
import PySide2.QtCore

from PySide2.QtGui import *
from PySide2.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTextEdit, QMainWindow
from PySide2.QtCore import Slot, Qt, QObject, QFile, QRectF, QPoint
from PySide2.QtUiTools import QUiLoader

import label_yolo_
from label_yolo_ import DatasetVerifier

#Remember to delete the first line of this file if you generate this file by using anaconda virtual env.
from window.ui_mainwindow import Ui_MainWindow 

'''
class MyWidget(QWidget):
    def __init__(self, ui_file, parent = None):
        #QWidget.__init__(self)
        super(MyWidget, self).__init__(parent)
        #super().__init__()

        
        #Load the widgets on UI
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        
        self.btn_next = self.window.btn_next 
        self.btn_prev = self.window.btn_prev
        self.btn_save = self.window.btn_save
        self.btn_delete = self.window.btn_delete
        self.btn_clear =self.window.btn_clear
        self.img_area = self.window.img_area
        self.act_openfile = self.window.act_openfile
        self.act_opendir = self.window.act_opendir
        
        # Connecting the signals
        self.btn_next.clicked.connect(self.test)
        self.btn_prev.clicked.connect(self.show_image)
        self.btn_save.clicked.connect(self.save_label)
        self.btn_delete.clicked.connect(self.delete_label)
        self.img_area.mousePressEvent = self.click_label
        #self.btn_exit.clicked.connect(self.close_window)
        self.act_openfile.triggered.connect(self.load_file)
        self.act_opendir.triggered.connect(self.open_dir)

        self.label_tool = label_yolo_.DatasetVerifier()

        self.window.show()


    def click_label(self, event):
        print("rrr")

    def mousePressEvent(self, QMouseEvent):
        #self.setDown(True)
        print(QMouseEvent.pos())
    
    def onMouseClicked(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.FirstCorner = (x, y)
            
        elif event == cv2.EVENT_LBUTTONUP:
            self.SecondCorner = (x, y)
            
            self.drawRectsAndDisplay()
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.deleteSelectedExistingRects((x, y)) == -1: # delete the newly drawn rect
                self.resetDrawing()
                
            self.drawRectsAndDisplay()
    
    @Slot()

    def test(self):
        print("sss")

    def show_image(self, image):
        self.img_area.setPixmap(image)

    def save_label(self, path):
        pass

    def delete_label(self, path):
        pass

    def close_window(self):
        sys.exit(app.exec_())

    def open_dir(self):
        selected_dir = QFileDialog.getExistingDirectory()
        return selected_dir

    def open_file(self):
        #filename = QFileDialog.getOpenFileName(self, self.tr("Open Image or Video"), self.tr("File (*.mp4 *.avi)"))
        #print(filename)
        
        dialog = QFileDialog(self)
        dialog.setNameFilter(self.tr("Images or Videos (*.jpg *.png *.mp4 *.avi)"))
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            filename = dialog.selectedFiles()
        return filename

    def load_file(self):
        file_path = self.open_file()[0]
        if file_path.endswith('.mp4') or file_path.endswith('.avi'):
            self.load_video(file_path)
        if file_path.endswith('.jpg') or file_path.endswith('.png'):
            self.show_image(file_path)
        
    def load_video(self, file_path):
        cap = cv2.VideoCapture(file_path)

        file_name = os.path.splitext(file_path)[0]
        if os.path.isdir(file_name) == True:
            shutil.rmtree(file_name)
        os.mkdir(file_name)

        total_frames = cap.get(7)
        success, _ = cap.read()
        count = 0
        if self.window.textedit_fps.toPlainText() != "":
            fps = self.window.textedit_fps.toPlainText()
        else:
            fps = cap.get(5)
        fps = int(fps)
        
        cap.set(CAP_PROP_POS_FRAMES, frame_index)


        while success:
            if count < total_frames:
                _, image = cap.read()
                if count % int(fps) == 0:
                    save_path = file_name + "/frame{}.jpg".format(str(count))
                    cv2.imwrite(save_path, image)
                count += 1
            else: 
                break
        cap.release()

        cvImg = self.label_tool.verifyDataset(file_name, 1.0 / 2)
        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.window.img_area.setPixmap(qImg)
'''


class MyWidget(QMainWindow):
    def __init__(self, parent = None):
        super(MyWidget, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Global variables
        self.frame_index = 0
        self.step = 1 #TODO: this params should be decided by user
        
        self.imgarea_width = 0
        self.imgarea_height = 0
        self.imgarea_pos = QPoint(0, 0)

        self.cursor_pos = QPoint(0, 0)
        
        # Connecting the signals
        #self.ui.btn_next("btn")
        self.ui.btn_next.clicked.connect(self.next_frame)
        self.ui.btn_prev.clicked.connect(self.prev_frame)
        self.ui.btn_save.clicked.connect(self.save_label)
        self.ui.btn_delete.clicked.connect(self.delete_label)
        #self.ui.img_area.mousePressEvent = self.click_label
        #self.btn_exit.clicked.connect(self.close_window)
        self.ui.act_openfile.triggered.connect(self.load_file)
        self.ui.act_opendir.triggered.connect(self.open_dir)

        self.ui.label_tool = label_yolo_.DatasetVerifier()

        #self.window.show()

    def mousePressEvent(self, event):
        #if event.type() == QtCore.QEvent.MouseButtonPress:
        if event.button() == Qt.LeftButton:
            print("left")
            print(self.ui.img_area.pos())
            print(self.ui.img_area.size())
            print(event.pos())
            self.cursor_pos = event.pos()
        if event.button() == Qt.RightButton:
            print("right")

    '''
    def onMouseClicked(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.FirstCorner = (x, y)
            
        elif event == cv2.EVENT_LBUTTONUP:
            self.SecondCorner = (x, y)
            
            self.drawRectsAndDisplay()
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.deleteSelectedExistingRects((x, y)) == -1: # delete the newly drawn rect
                self.resetDrawing()
                
            self.drawRectsAndDisplay()
    '''

    @Slot()

    def next_frame(self):
        self.wait = False
        if (self.frame_index + self.step) > self.total_frames:
            return
        else:
            self.frame_index += self.step

    def prev_frame(self):
        self.wait = False
        #self.keep_loading = False
        if self.frame_index == 0:
            return
        self.frame_index -= self.step

    def show_image(self, image):
        pass

    def save_label(self, path):
        self.keep_labeling = False

    def delete_label(self, path):
        pass

    def close_window(self):
        sys.exit(app.exec_())

    def open_dir(self):
        selected_dir = QFileDialog.getExistingDirectory()
        return selected_dir

    def open_file(self):
        #filename = QFileDialog.getOpenFileName(self, self.tr("Open Image or Video"), self.tr("File (*.mp4 *.avi)"))
        #print(filename)
        
        dialog = QFileDialog(self)
        dialog.setNameFilter(self.tr("Images or Videos (*.jpg *.png *.mp4 *.avi *.mkv)"))
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            filename = dialog.selectedFiles()
        return filename

    def load_file(self):
        self.file_path = self.open_file()[0]
        if self.file_path.endswith('.mp4') or self.file_path.endswith('.avi') or self.file_path.endswith('.mkv'):
            self.clear_history()
            self.load_video()
        if self.file_path.endswith('.jpg') or self.file_path.endswith('.png'):
            self.show_image(self.file_path)
    
    def clear_history(self):
        self.frame_index = 0
        self.real_frame_index = 0


    def load_video(self):
        
        self.file_name = os.path.splitext(self.file_path)[0]
        #Delete old data if it exists
        if os.path.isdir(self.file_name) == True:
            shutil.rmtree(self.file_name)
        try:
            os.mkdir(self.file_name)
        except:
            print("close folder first!")
        #TODO: let user to decide weather to keep old data

        self.keep_labeling = True # set keep_labeling as False after finished labeling work
        while self.keep_labeling:
            self.open_cap()

        '''
        while success:
            if count <= total_frames:
                _, image = cap.read()
                if count % int(fps) == 0:
                    save_path = file_name + "/frame{}.jpg".format(str(count))
                    cv2.imwrite(save_path, image)
                    #self.ui.img_area.setPixmap(save_path)
                    i = cv2.imread(save_path)
                    cv2.imshow('image', i)
                count += 1

                key = cv2.waitKey(0)

            else: 
                break
        
        cvImg = self.label_tool.verifyDataset(file_name, 1.0 / 2)
        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.ui.img_area.setPixmap(qImg)
        '''
    def open_cap(self):
        self.cap = cv2.VideoCapture(self.file_path)
        self.total_frames = self.cap.get(7)
        self.num_digits = len(str(int(self.total_frames)))
        #success, _ = cap.read()
        self.count = 0 #TODO: count should start from current frame index

        if self.ui.textedit_fps.toPlainText() != "":
            fps = self.ui.textedit_fps.toPlainText()
        else:
            fps = self.cap.get(5)
        fps = int(fps)

        self.keep_loading = True
        
        while self.keep_loading:
            self.load_one_frame()
            self.wait = True
            while self.wait:
                qApp.processEvents()
                time.sleep(0.05)
        #TODO: load label from text file

        self.cap.release()
        print("unlocked")

    def load_bbox():
        pass



    def load_one_frame(self):
        #get the size of current image area
        self.imgarea_width = self.ui.img_area.width()
        self.imgarea_height = self.ui.img_area.height()
        self.imgarea_pos = self.ui.img_area.pos()

        if self.frame_index < 0:
            print("Error: index < 0")
            return
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
        self.real_frame_index = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        #for i in range(self.step):
            #self.cap.grab()
        #self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
        #f = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        
        ret, cur_img = self.cap.read()
        #ret, cur_img = self.cap.retrieve()

        if self.frame_index != self.real_frame_index:
            print("Error: Read wrong frame!!!  Expect: " + str(self.frame_index) + " Real: " + str(int(self.real_frame_index)))
        else:
            print("Read correctly  Expect: " + str(self.frame_index) + " Real: " + str(int(self.real_frame_index)))
        
        if ret == True:
            save_path = self.file_name + "/frame{}.jpg".format(str(self.frame_index).zfill(self.num_digits))
            if os.path.isfile(save_path) == False:
                cv2.imwrite(save_path, cur_img) 
            pixmap = QPixmap(save_path)
            self.res_pixmap = pixmap.scaled(self.ui.img_area.width(), self.ui.img_area.height(), Qt.KeepAspectRatio)
            self.ui.img_area.setAlignment(Qt.AlignCenter)
            #TODO: reszie image size dynamically
            res_width = self.res_pixmap.width()
            res_height = self.res_pixmap.height()
            
            if res_width == self.imgarea_width:
                res_pos_x = self.imgarea_pos.x()
                res_pos_y = self.imgarea_pos.y() + self.imgarea_height/2 - res_height/2
                print("width", res_pos_x, res_pos_y)
            elif res_height == self.imgarea_height:
                res_pos_x = self.imgarea_pos.x() + self.imgarea_width/2 - res_width/2
                res_pos_y = self.imgarea_pos.y()
                print("height", res_pos_x, res_pos_y)

            bbox_pos_x = self.cursor_pos.x()-res_pos_x
            bbox_pos_y = self.cursor_pos.y()-res_pos_y
            rect = QRectF(bbox_pos_x, bbox_pos_y, res_width/2, res_height/2) 
            #TODO: if window size changes, QRec size should change accordingly. So need to calculate the ratio. 
            painter = QPainter(self.res_pixmap)
            painter.setPen(QPen(Qt.blue, 2))
            
            painter.drawRect(rect)
            self.ui.img_area.setPixmap(self.res_pixmap)
            
    '''
    def paintEvent(self, event):
        rect = QRectF(100,100,200,200)
        painter = QPainter(self.res_pixmap)
        painter.setPen(QPen(Qt.blue, 5))
        
        painter.drawRect(rect)
    '''
    def unlock_loop(self):
        self.wait = False

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    #label_tool = label_yolo_.DatasetVerifier()
    widget.show()
    sys.exit(app.exec_())