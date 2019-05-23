import os
import cv2
import time
import sys
import random
import shutil
import numpy as np
import PySide2.QtCore
import copy

from PySide2.QtGui import *
from PySide2.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTextEdit, QMainWindow
from PySide2.QtCore import Slot, Qt, QObject, QFile, QRectF, QPoint
from PySide2.QtUiTools import QUiLoader

#import label_yolo_
#from label_yolo_ import DatasetVerifier

#Remember to delete the first line of this file if you generate this file using anaconda virtual env.
from window.ui_mainwindow import Ui_MainWindow 
from annotation_yolo import AnnotationYOLO

class AppWindow(QMainWindow):
    def __init__(self, parent = None):
        super(AppWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.annotation_format = None

        #Global variables
        self.frame_index = 0
        self.step = 1 #TODO: this params should be decided by user
        
        self.imgarea_width = 0
        self.imgarea_height = 0
        self.imgarea_pos = QPoint(0, 0)
        #self.centralWidget_pos = self.ui.centralWidget.pos()
        #self.event_pos = QPoint(0, 0)
        self.lefttop_corner = QPoint(0, 0)
        self.rightbottom_corner = QPoint(0, 0)
        self.cursor_pos = QPoint(0, 0)

        #rects
        self.saved_rects = [] 
        self.unsaved_rects = []
        self.selected_rect = []

        # Connecting the signals
        #self.ui.btn_next("btn")
        self.ui.btn_next.clicked.connect(self.next_frame)
        self.ui.btn_prev.clicked.connect(self.prev_frame)
        self.ui.btn_save.clicked.connect(self.save_label)
        self.ui.btn_delete.clicked.connect(self.delete_label)
        self.ui.btn_clear.clicked.connect(self.clear_label)
        #self.ui.img_area.mousePressEvent = self.click_label
        
        self.ui.act_openfile.triggered.connect(self.load_file)
        self.ui.act_opendir.triggered.connect(self.load_dir)

        #self.ui.label_tool = label_yolo_.DatasetVerifier()
        #self.ui.img_area.setMouseTracking(True)
        #self.window.show()
        
    def mousePressEvent(self, event):
        #if event.type() == QtCore.QEvent.MouseButtonPress:
        if event.button() == Qt.LeftButton:
            print("left")
            print(self.ui.img_area.pos())
            print(event.pos())
            self.lefttop_corner = event.pos()
        if event.button() == Qt.RightButton:
            self.cursor_pos = event.pos()
            print("right:  ", self.cursor_pos.x(), self.cursor_pos.y())
    
    def mouseMoveEvent(self, event):
        #self.rightbottom_corner = event.pos()
        x = self.rightbottom_corner.x()
        y = self.rightbottom_corner.y()
        #print("-- ", x, y)

        #TODO: update rect while mouse moving
        #self.clear_rects()
        #self.calculate_bbox_pos()
        #self.draw_img()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            #self.clear_rects()
            self.rightbottom_corner = event.pos()
            self.scale_img()
            self.calculate_bbox_pos()
            self.draw_img()
        if event.button() == Qt.RightButton:
            self.selected_rect = []

            self.selected_saved_rect_index, self.selected_unsaved_rect_index = self.find_selected_bbox(self.cursor_pos.x(), self.cursor_pos.y())
            self.draw_img()
    
    #TODO: creating a new area which contains the categories of labels; if no label is chosen, return nothing.

    def resizeEvent(self, event):
        if self.ui.img_area.pixmap():
            self.scale_img()
            #self.calculate_bbox_pos()
            self.draw_img()

    @Slot()

    def next_frame(self):
        self.wait = False

        #clear the container of rects
        self.unsaved_rects = []
        self.saved_rects = []

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

    def load_image(self, image):
        pass

    def save_label(self):
        self.keep_labeling = False
        for item in self.unsaved_rects:
            self.saved_rects.append(item)
        self.unsaved_rects = []
        self.draw_img()
        self.annotation_format.write_label(self.saved_rects, self.label_path)    
        #TODO: add category into saved_rects

    def delete_label(self):
        if self.selected_saved_rect_index != -1:
            del self.saved_rects[self.selected_saved_rect_index]
        if self.selected_unsaved_rect_index != -1:
            del self.unsaved_rects[self.selected_unsaved_rect_index]
        self.selected_saved_rect_index = self.selected_unsaved_rect_index = -1
        self.selected_rect = []
        self.draw_img()
    
    def clear_label(self):
        self.saved_rects = []
        self.unsaved_rects = []
        self.draw_img()

    def find_selected_bbox(self, x, y):
        saved_rect_index = unsaved_rect_index = -1
        for i in range(len(self.saved_rects)):
            if x > (self.res_width * self.saved_rects[i][0] + self.res_pos_x) and \
                x < (self.res_width * self.saved_rects[i][0] + self.res_width * self.saved_rects[i][2] + self.res_pos_x) and \
                y > (self.res_height * self.saved_rects[i][1] + self.res_pos_y) and \
                y < (self.res_height * self.saved_rects[i][1] + self.res_height * self.saved_rects[i][3] + self.res_pos_y):
                saved_rect_index = i
                self.selected_rect.append(self.saved_rects[i])
                break
        for j in range(len(self.unsaved_rects)):
            if x > (self.res_width * self.unsaved_rects[j][0] + self.res_pos_x) and \
                x < (self.res_width * self.unsaved_rects[j][0] + self.res_width * self.unsaved_rects[j][2] + self.res_pos_x) and \
                y > (self.res_height * self.unsaved_rects[j][1] + + self.res_pos_y) and \
                y < (self.res_height * self.unsaved_rects[j][1] + self.res_height * self.unsaved_rects[j][3] + self.res_pos_y):
                unsaved_rect_index = j
                self.selected_rect.append(self.unsaved_rects[j])
                break
        if saved_rect_index == -1 and unsaved_rect_index == -1:
            self.selected_rect = []
        return saved_rect_index, unsaved_rect_index
        #TODO: assumimg no rects overlap for now, need to handle overlaping situation.

    def close_window(self):
        sys.exit(app.exec_())

    def open_dir(self):
        try:
            selected_dir = QFileDialog.getExistingDirectory()
            return selected_dir
        except:
            return None
        

    def open_file(self):
        #filename = QFileDialog.getOpenFileName(self, self.tr("Open Image or Video"), self.tr("File (*.mp4 *.avi)"))
        #print(filename)
        
        dialog = QFileDialog(self)
        dialog.setNameFilter(self.tr("Images or Videos (*.jpg *.png *.mp4 *.avi *.mkv)"))
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            try:
                filename = dialog.selectedFiles()
                return filename
            except:
                return None
            
    def load_file(self):
        _file_path = self.open_file()
        if _file_path:

            self.file_path = _file_path[0]
            if self.file_path.endswith('.mp4') or self.file_path.endswith('.avi') or self.file_path.endswith('.mkv'):
                self.clear_history()
                self.load_video()
            if self.file_path.endswith('.jpg') or self.file_path.endswith('.png'):
                self.load_image(self.file_path)
        else:
            print("no file is selected!")

    def load_dir(self):
        _file_dir = self.open_dir()
        if _file_dir:
            self.file_dir = _file_dir
            self.file_names = []
            for filename in os.listdir(_file_dir):
                if os.path.splitext(filename)[-1] == ".jpg" or os.path.splitext(filename)[-1] == ".png": 
                    self.file_names.append(filename)

                    txt_name = os.path.splitext(filename)[0]+".txt"
                    label_path = os.path.join(self.file_dir, txt_name).replace('\\', '/')
                
                    if not os.path.isfile(label_path):
                        f = open(label_path, "w")
                        f.close()

            if self.file_names:
                self.keep_loading = True    
                while self.keep_loading:
                    self.read_image()
                    self.wait = True
                    while self.wait:
                        qApp.processEvents()
                        time.sleep(0.05)
            else:
                print("The directory is empty")

    def clear_history(self):
        self.frame_index = 0
        self.real_frame_index = 0

    def load_video(self):
        self.file_path_without_ext = os.path.splitext(self.file_path)[0]
        self.file_name = os.path.split(self.file_path_without_ext)[-1]
        #Delete old data if it exists
        if os.path.isdir(self.file_path_without_ext) == True:
            shutil.rmtree(self.file_path_without_ext)
        try:
            os.mkdir(self.file_path_without_ext)
        except:
            print("close folder first!")
        #TODO: let user to decide weather to keep old data

        self.keep_labeling = True # set keep_labeling as False after finished labeling work
        while self.keep_labeling:
            self.open_cap()

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
            self.read_frame_from_video()
            self.wait = True
            while self.wait:
                qApp.processEvents()
                time.sleep(0.05)

        self.cap.release()
        print("unlocked")

    def load_bbox():
        pass

    def read_frame_from_video(self):
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
            img_name = self.file_name + "_frame{}.jpg".format(str(self.frame_index).zfill(self.num_digits))
            label_name = self.file_name + "_frame{}.txt".format(str(self.frame_index).zfill(self.num_digits))
            self.img_path = os.path.join(self.file_path_without_ext, img_name)
            self.label_path = os.path.join(self.file_path_without_ext, label_name)
            if not os.path.isfile(self.label_path):
                f = open(self.label_path, "w")
                f.close()
            
            if os.path.isfile(self.img_path) == False:
                cv2.imwrite(self.img_path, cur_img) 
            self.raw_pixmap = QPixmap(self.img_path)
            #self.raw_pixmap_copy = self.raw_pixmap.copy()

            #read label

            self.scale_img()
            self.calculate_bbox_pos()    
            self.draw_img()
    
    def read_image(self):
        self.total_frames = len(self.file_names)
        if self.frame_index < self.total_frames:
            cur_img_name = self.file_names[self.frame_index]
            self.img_path = os.path.join(self.file_dir, cur_img_name).replace('\\', '/')
            image = QPixmap(self.img_path)
            self.raw_pixmap = image.copy()

            txt_name = os.path.splitext(cur_img_name)[0] + ".txt"
            self.label_path = os.path.join(self.file_dir, txt_name).replace('\\', '/')
            self.saved_rects = self.annotation_format.read_label(self.label_path)

            self.scale_img()
            self.calculate_bbox_pos()    
            self.draw_img()

    def scale_img(self):
        self.imgarea_width = self.ui.img_area.width()
        self.imgarea_height = self.ui.img_area.height()

        self.imgarea_pos = self.ui.img_area.pos()

        self.res_pixmap = self.raw_pixmap.scaled(self.ui.img_area.width(), self.ui.img_area.height(), Qt.KeepAspectRatio)
        self.ui.img_area.setAlignment(Qt.AlignCenter)

        self.res_width = self.res_pixmap.width()
        self.res_height = self.res_pixmap.height()

        if self.res_width == self.imgarea_width:
            self.centralWidget_pos = self.ui.centralWidget.pos()
            self.res_pos_x = self.centralWidget_pos.x() + self.imgarea_pos.x()
            self.res_pos_y = self.centralWidget_pos.y() + self.imgarea_pos.y() + self.imgarea_height/2 - self.res_height/2
            print("width", self.res_pos_x, self.res_pos_y)
        elif self.res_height == self.imgarea_height:
            self.centralWidget_pos = self.ui.centralWidget.pos()
            self.res_pos_x = self.imgarea_pos.x() + self.imgarea_width/2 - self.res_width/2
            self.res_pos_y = self.centralWidget_pos.y() + self.imgarea_pos.y()
            print("height", self.res_pos_x, self.res_pos_y)

    def calculate_bbox_pos(self):
        self.bbox_pos_x = self.lefttop_corner.x()-self.res_pos_x
        self.bbox_pos_y = self.lefttop_corner.y()-self.res_pos_y
        self.bbox_width = self.rightbottom_corner.x() - self.lefttop_corner.x()
        self.bbox_height = self.rightbottom_corner.y() - self.lefttop_corner.y()
        self.lefttop_corner = QPoint(0, 0)
        self.rightbottom_corner = QPoint(0, 0)

        self.calculate_bbox_ratio()
        self.save_bbox_ratio()

    def calculate_bbox_ratio(self):
        self.bbox_pos_x_ratio = self.bbox_pos_x / self.res_width
        self.bbox_pos_y_ratio = self.bbox_pos_y / self.res_height
        self.bbox_width_ratio = self.bbox_width / self.res_width
        self.bbox_height_ratio = self.bbox_height / self.res_height
        #TODO: keep 7 digits only

    def save_bbox_ratio(self):
        if self.bbox_pos_x_ratio >= 0 and self.bbox_pos_y_ratio >= 0:
            lst = []
            lst.append(self.bbox_pos_x_ratio)
            lst.append(self.bbox_pos_y_ratio)
            lst.append(self.bbox_width_ratio)
            lst.append(self.bbox_height_ratio)
            self.unsaved_rects.append(lst)
        #TODO: if don't click on image, don't save coordinates.     

    def draw_img(self):
        image = self.res_pixmap.copy()
        painter = QPainter(image)
        if self.saved_rects:
            for item in self.saved_rects:
                painter.setPen(QPen(Qt.green, 2))
                _bbox_pos_x = self.res_width * item[0]
                _bbox_pos_y = self.res_height * item[1] 
                _bbox_width = self.res_width * item[2]
                _bbox_height = self.res_height * item[3]
                self.rect = QRectF(_bbox_pos_x, _bbox_pos_y, _bbox_width, _bbox_height)
                painter.drawRect(self.rect)
        if self.unsaved_rects:
            for item in self.unsaved_rects:
                painter.setPen(QPen(Qt.green, 1, Qt.DashDotDotLine))
                _bbox_pos_x = self.res_width * item[0]
                _bbox_pos_y = self.res_height * item[1]
                _bbox_width = self.res_width * item[2]
                _bbox_height = self.res_height * item[3]
                self.rect = QRectF(_bbox_pos_x, _bbox_pos_y, _bbox_width, _bbox_height)
                painter.drawRect(self.rect)
        if self.selected_rect:
            for item in self.selected_rect:
                painter.setPen(QPen(Qt.gray, 2, Qt.DotLine))
                _bbox_pos_x = self.res_width * item[0]
                _bbox_pos_y = self.res_height * item[1]
                _bbox_width = self.res_width * item[2]
                _bbox_height = self.res_height * item[3]
                self.rect = QRectF(_bbox_pos_x, _bbox_pos_y, _bbox_width, _bbox_height)
                painter.drawRect(self.rect)
        self.ui.img_area.setPixmap(image)
        painter.end()

    def clear_rects(self):
        #self.painter.end()
        #self.pixmap = self.raw_img.copy()
        #self.ui.img_area.clear()
        #print("clear")
        pass

    def unlock_loop(self):
        self.wait = False

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app_window = AppWindow()
    app_window.annotation_format = AnnotationYOLO()
    app_window.show()

    sys.exit(app.exec_())


#TODO: 1. multi bboxes
#      2. multi labels