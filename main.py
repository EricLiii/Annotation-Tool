#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on June 2019

@author: Zefeng
"""
#put most of the code in one file because I'm too lazy to split and optimize it :)

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
from PySide2.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, \
                              QTextEdit, QMainWindow, QTableWidget, QTableWidgetItem, QColorDialog, \
                              QPlainTextEdit, QWidget, QTextEdit, QDialog
from PySide2.QtCore import Slot, Qt, QObject, QFile, QRectF, QPoint, QEvent
from PySide2.QtUiTools import QUiLoader

#Remember to delete the first line of ui_xxxxxx.py file if you generate this file using anaconda virtual env.
from AppWindow.ui_mainwindow import Ui_MainWindow 
from SecWindow.ui_dialog import Ui_Dialog
from annotation_yolo import AnnotationYOLO

from functools import partial

class AppWindow(QMainWindow):
    def __init__(self, parent = None):
        super(AppWindow, self).__init__(parent)
        #Load UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Annotation Tool")
        self.annotation_format = None

        #Initialization
        self.wiring_signal_slot()
        self.init_params()
        self.init_rects()
        self.init_ui()
        self.init_color_dic()

    def init_rects(self):
        # Init rects which contains rects during labeling.
        self.saved_rects = [] 
        self.unsaved_rects = []
        self.selected_rect = []

    def init_params(self):
        # Init some params
        self.current_category_index = -1
        self.current_category_id = -1
        self.current_category_name = ""
        self.category_color_dic = {}
        self.id_str = ""

        self.status_content = ""

        self.keep_loading = False

        self.frame_index = 0
        self.frame_step = 1 
        
        self.imgarea_width = 0
        self.imgarea_height = 0
        self.imgarea_pos = QPoint(0, 0)
        self.lefttop_corner = QPoint(0, 0)
        self.rightbottom_corner = QPoint(0, 0)
        self.cursor_pos = QPoint(0, 0)

        self.is_mouse_moving = False

    def init_color_dic(self):     
        #Contains default colors for labeling if user doesn't set any color.
        self.category_defaultcolor_dic = {0: QColor(255, 0, 0), 1: QColor(0, 255, 0), 2: QColor(0, 0, 255), 3: QColor(0, 255, 204), 4: QColor(102, 153, 0), 
                                          5: QColor(153, 102, 0), 6: QColor(255, 255, 0), 7: QColor(204, 204, 255), 8: QColor(102, 0, 255), 9: QColor(255, 0, 255), 
                                          10: QColor(128, 0, 0), 11: QColor(0, 51, 0), 12: QColor(255, 153, 102), 13: QColor(102, 153, 153), 14: QColor(204, 204, 0),
                                          15: QColor(0, 0, 0)}
    
    def init_ui(self):
        #Add addtional UI setting
        self.ui.tableWidget_categories.setColumnCount(2)
        self.ui.tableWidget_categories.setColumnWidth(0, 30)
        self.ui.tableWidget_categories.setColumnWidth(1, 98)
        self.ui.tableWidget_categories.insertRow(0)
        self.ui.tableWidget_categories.setSpan(0, 0, 1, 2)
        first_row = QTableWidgetItem("     Category Name")
        first_row.setFlags(False)
        self.ui.tableWidget_categories.setItem(0, 0, first_row)
        self.ui.tableWidget_categories.setVerticalHeaderItem(0, QTableWidgetItem(""))

    def wiring_signal_slot(self):
        # Wiring signals and slots
        self.ui.btn_next.clicked.connect(self.next_frame)
        self.ui.btn_back.clicked.connect(self.prev_frame)
        self.ui.btn_save.clicked.connect(partial(self.save_label, 0))
        self.ui.btn_deleteSelected.clicked.connect(self.delete_label)
        self.ui.btn_deleteUnsaved.clicked.connect(self.delete_unsaved)
        self.ui.btn_deleteAll.clicked.connect(self.clear_label)
        self.ui.btn_applyCategory.clicked.connect(self.apply_category)
        self.ui.btn_chooseColor.clicked.connect(self.choose_color)
        self.ui.btn_addCategory.clicked.connect(self.add_category)
        self.ui.btn_deleteCategory.clicked.connect(self.delete_category)
        self.ui.btn_refresh.clicked.connect(self.refresh_image)
        self.ui.btn_saveCategory.clicked.connect(self.save_category_name)
        self.ui.btn_applySetting.clicked.connect(self.apply_frame_setting)
        self.ui.tableWidget_categories.cellClicked.connect(self.cell_clicked)
        self.ui.act_openfile.triggered.connect(self.choose_file)
        self.ui.act_opendir.triggered.connect(self.choose_dir)
        self.ui.act_openUsage.triggered.connect(self.sec_window)

    def sec_window(self):
        self.sec_window = SecWindow()
        self.sec_window.setWindowTitle("Annotation Tool Usage")
        self.sec_window.show()

    def mousePressEvent(self, event):
        if self.ui.img_area.pixmap():
            if event.button() == Qt.LeftButton:
                print("left")
                print(self.ui.img_area.pos())
                print(event.pos())
                self.is_mouse_moving = True
                self.lefttop_corner = event.pos()
            if event.button() == Qt.RightButton:
                self.cursor_pos = event.pos()
                print("right:  ", self.cursor_pos.x(), self.cursor_pos.y())
    
    def mouseMoveEvent(self, event):
        if self.ui.img_area.pixmap():
            self.rightbottom_corner = event.pos()
            self.scale_img()
            self.calculate_bbox_pos()
            self.draw_img()
            if self.lefttop_corner != self.rightbottom_corner:
                self.unsaved_rects.pop()    

    def mouseReleaseEvent(self, event):
        self.is_mouse_moving = False
        if self.ui.img_area.pixmap():
            if event.button() == Qt.LeftButton:
                self.rightbottom_corner = event.pos()
                if self.lefttop_corner != self.rightbottom_corner:
                    self.selected_rect = []
                    self.scale_img()
                    self.calculate_bbox_pos()
                    try:
                        if self.unsaved_rects[-1][0] > -1:
                            self.selected_unsaved_rect_index = self.newly_draw_rect_index
                            self.selected_rect.append(self.unsaved_rects[self.selected_unsaved_rect_index])
                            #self.selected_saved_rect_index, self.selected_unsaved_rect_index = self.find_selected_bbox(event.x(), event.y())
                        else:
                            self.unsaved_rects.pop()
                        self.draw_img()
                    except:
                        pass
            if event.button() == Qt.RightButton:
                self.selected_rect = []

                self.selected_saved_rect_index, self.selected_unsaved_rect_index = self.find_selected_bbox(self.cursor_pos.x(), self.cursor_pos.y())
                self.draw_img()
                self.ui.tableWidget_categories.clearFocus()

    def resizeEvent(self, event):
        if self.ui.img_area.pixmap():
            self.scale_img()
            #self.calculate_bbox_pos()
            self.draw_img()

    def keyPressEvent(self, event):
        keyboard_dic = {Qt.Key_0: "0", Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3", Qt.Key_4: "4", 
                        Qt.Key_5: "5", Qt.Key_6: "6", Qt.Key_7: "7", Qt.Key_8: "8", Qt.Key_9: "9" }
        if event.key() in keyboard_dic and self.selected_rect:
            self.id_str += keyboard_dic[event.key()]
        elif event.key() == Qt.Key_B:
            self.prev_frame()  
        elif event.key() == Qt.Key_N:
            self.next_frame()
        elif event.key() == Qt.Key_S:
            self.save_label(0)
        elif event.key() == Qt.Key_D:
            self.delete_label()
        elif event.key() == Qt.Key_E and self.selected_rect:
            if self.id_str != "":
                if self.selected_saved_rect_index != -1:
                    self.saved_rects[self.selected_saved_rect_index][0] = int(self.id_str)
                    self.save_label(0)
                elif self.selected_unsaved_rect_index != -1:
                    self.unsaved_rects[self.selected_unsaved_rect_index][0] = int(self.id_str)
                self.draw_img()
                self.id_str = ""
            else:
                print("please input id first")
        else:
            self.id_str = ""

    def show_info(self, target_widget, new_info):
        """
        Print info on UI
        """
        if isinstance(target_widget, QTextEdit):
            target_widget.append(new_info)
        elif isinstance(target_widget, QLabel):
            target_widget.setText(new_info)
        else:
            pass
        
    @Slot()

    def next_frame(self):
        try:
            self.wait = False
            self.unsaved_rects = []
            self.saved_rects = []
            self.selected_rect = []
            if (self.frame_index + self.frame_step) > self.total_frames:
                return
            else:
                self.frame_index += self.frame_step
        except:
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Frame ndex or frame step is empty!")

    def prev_frame(self):
        try:
            self.selected_rect = []
            self.wait = False
            #self.keep_loading = False
            if self.frame_index == 0:
                return
            self.frame_index -= self.frame_step
        except:
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> No previous frame!")

    def save_label(self, flag):
        """
        If flag == 0, save all rects(including unsaved rects); 
        If flag == 1, update saved rects only(keep unsaved rects unsaved).
        """
        try:
            self.keep_labeling = False
            if flag == 0:
                for item in self.unsaved_rects:
                    self.saved_rects.append(item)
                self.unsaved_rects = []
            self.draw_img()
            self.annotation_format.write_label(self.saved_rects, self.label_path)   
            if flag == 0: 
                self.show_info(self.ui.textEdit_statusBar, self.img_path + "   Saved successfully!")
        except:
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Nothing to save!")

    def delete_label(self):
        try:
            if self.selected_saved_rect_index != -1:
                # if delete a saved rect, revise label, too.
                del self.saved_rects[self.selected_saved_rect_index]
                self.save_label(1)
            if self.selected_unsaved_rect_index != -1:
                # if delete a unsaved rect, no need to revise label file.
                del self.unsaved_rects[self.selected_unsaved_rect_index]
            self.selected_saved_rect_index = self.selected_unsaved_rect_index = -1
            self.selected_rect = []
            self.draw_img()
        except:
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Nothing to delete!")
    
    def delete_unsaved(self):
        try:
            self.unsaved_rects = []
            self.selected_rect = []
            self.draw_img()
        except:
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Nothing to delete!")

    def clear_label(self):
        try:
            self.saved_rects = []
            self.unsaved_rects = []
            self.selected_rect = []
            self.save_label(0)
            self.draw_img()
        except:
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Nothing to clear!")

    def apply_category(self):
        try:
            self.current_category_id = int(self.ui.tableWidget_categories.verticalHeaderItem(self.current_category_index).text())
        except:
            print("no text")
        current_item = self.ui.tableWidget_categories.currentItem()
        try:
           self.current_category_name = current_item.text()    
        except:
            self.show_info(self.ui.textEdit_statusBar, "Name is empty!")

        if self.current_category_id != -1:
            if self.selected_saved_rect_index != -1:
                self.saved_rects[self.selected_saved_rect_index][0] = int(self.current_category_id)
                self.save_label(0)
            elif self.selected_unsaved_rect_index != -1:
                self.unsaved_rects[self.selected_unsaved_rect_index][0] = int(self.current_category_id)
            self.draw_img()
   
    def choose_color(self):
        try:
            color = QColorDialog.getColor()
        except:
            print("No color selected!")

        if color.isValid() and self.current_category_index != -1:
            self.category_color_dic[self.current_category_id] = color
            item = self.ui.tableWidget_categories.item(self.current_category_index, 0)
            item.setBackground(QBrush(self.category_color_dic[self.current_category_id]))

    def add_category(self):
        row_numbers = self.ui.tableWidget_categories.rowCount()
        self.ui.tableWidget_categories.insertRow(row_numbers)
        first_item = QTableWidgetItem()
        second_item = QTableWidgetItem()
        self.ui.tableWidget_categories.setItem(row_numbers, 0, first_item)
        self.ui.tableWidget_categories.setItem(row_numbers, 1, second_item)

        if row_numbers == 1:
            new_header_text = '0'
        else:
            header = self.ui.tableWidget_categories.verticalHeaderItem(row_numbers - 1)
            last_header_text = header.text()
            new_header_text = str(int(last_header_text) + 1)
            
        try:
            item = self.ui.tableWidget_categories.item(1, 0)
            item.setBackground(QBrush(self.category_color_dic[self.current_category_id]))
        except:
            print("no item")
        self.ui.tableWidget_categories.setVerticalHeaderItem(row_numbers, QTableWidgetItem(new_header_text))
        
    def cell_clicked(self):
        self.current_category_index = self.ui.tableWidget_categories.currentRow()
        self.current_category_id = int(self.ui.tableWidget_categories.verticalHeaderItem(self.current_category_index).text())
        self.ui.tableWidget_categories.setFocus()
        print(self.current_category_index)

    def delete_category(self):
        self.ui.tableWidget_categories.removeRow(self.current_category_index)

    def refresh_image(self):
        self.draw_img()

    def apply_frame_setting(self):
        if not self.keep_loading:
            return
        start_frame = self.ui.plainTextEdit_startFrame.toPlainText()
        frame_step = self.ui.plainTextEdit_frameStep.toPlainText()
        if start_frame and start_frame != "N.A.":
            try:
                self.frame_index = int(start_frame)
            except:
                print("wrong start frame!")
                self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Wrong start frame!")
                return
        if frame_step and frame_step != "N.A.":
            try:
                self.frame_step = int(frame_step)
            except:
                print("wrong frame step!")     
                self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Wrong frame step!")  
                return
        self.frame_index -= self.frame_step
        self.next_frame()

    def clear_category_area(self):
        row_no = self.ui.tableWidget_categories.rowCount()
        for i in reversed(range(1, row_no)):
            self.ui.tableWidget_categories.removeRow(i)  

    def find_selected_bbox(self, x, y):
        saved_rect_index = unsaved_rect_index = -1
        min_saved_bbox_size = min_unsaved_bbox_size = 0

        for i in range(len(self.saved_rects)):
            if x >= (self.res_width * self.saved_rects[i][1][0] + self.res_pos_x) and \
                x <= (self.res_width * self.saved_rects[i][1][0] + self.res_width * self.saved_rects[i][1][2] + self.res_pos_x) and \
                y >= (self.res_height * self.saved_rects[i][1][1] + self.res_pos_y) and \
                y <= (self.res_height * self.saved_rects[i][1][1] + self.res_height * self.saved_rects[i][1][3] + self.res_pos_y):
                
                bbox_size = self.saved_rects[i][1][2] * self.saved_rects[i][1][3]
                if min_saved_bbox_size == 0:
                    min_saved_bbox_size = bbox_size
                    saved_rect_index = i
                elif min_saved_bbox_size > bbox_size:
                    min_saved_bbox_size = bbox_size
                    saved_rect_index = i
                else:
                    continue
                    
        for j in range(len(self.unsaved_rects)):
            if x >= (self.res_width * self.unsaved_rects[j][1][0] + self.res_pos_x) and \
                x <= (self.res_width * self.unsaved_rects[j][1][0] + self.res_width * self.unsaved_rects[j][1][2] + self.res_pos_x) and \
                y >= (self.res_height * self.unsaved_rects[j][1][1] + + self.res_pos_y) and \
                y <= (self.res_height * self.unsaved_rects[j][1][1] + self.res_height * self.unsaved_rects[j][1][3] + self.res_pos_y):

                bbox_size = self.unsaved_rects[j][1][2] * self.unsaved_rects[j][1][3]
                if min_unsaved_bbox_size == 0:
                    min_unsaved_bbox_size = bbox_size
                    unsaved_rect_index = j
                elif min_unsaved_bbox_size > bbox_size:
                    min_unsaved_bbox_size = bbox_size
                    unsaved_rect_index = j
                else:
                    continue

        if saved_rect_index != -1 and unsaved_rect_index == -1:
            self.selected_rect.append(self.saved_rects[saved_rect_index])
        elif unsaved_rect_index != -1 and saved_rect_index == -1:
            self.selected_rect.append(self.unsaved_rects[unsaved_rect_index])
        elif saved_rect_index == -1 and unsaved_rect_index == -1:
            self.selected_rect = []
        elif saved_rect_index != -1 and unsaved_rect_index != -1:
            if min_saved_bbox_size > min_unsaved_bbox_size:
                self.selected_rect.append(self.unsaved_rects[unsaved_rect_index])
                saved_rect_index = -1
            else:
                self.selected_rect.append(self.saved_rects[saved_rect_index])
                unsaved_rect_index = -1
        return saved_rect_index, unsaved_rect_index

    def close_window(self):
        sys.exit(app.exec_())

    def open_dir(self):
        try:
            selected_dir = QFileDialog.getExistingDirectory()
            return selected_dir
        except:
            return None
        
    def choose_file(self):
        _file_path = self.open_file()
        if _file_path:

            self.file_path = _file_path[0]
            if self.file_path.endswith('.mp4') or self.file_path.endswith('.avi') or self.file_path.endswith('.mkv'):
                self.set_frame_setting(0)
                self.load_video()
            #if self.file_path.endswith('.jpg') or self.file_path.endswith('.png'):
            #    self.load_image(self.file_path)
        else:
            print("no file is selected!")

    def choose_dir(self):
        _file_dir = self.open_dir()
        parent_dir = os.path.dirname(_file_dir)

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
                self.category_name_file_path = parent_dir + "/category.name"
                self.load_category_name(self.category_name_file_path)
                self.set_frame_setting(1)
                self.clear_history()
                self.keep_loading = True    
                while self.keep_loading:
                    self.read_image()
                    self.wait = True
                    while self.wait:
                        qApp.processEvents()
                        time.sleep(0.05)
            else:
                print("The directory is empty")

    def open_file(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter(self.tr("Images or Videos (*.jpg *.png *.mp4 *.avi *.mkv)"))
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            try:
                filename = dialog.selectedFiles()
                return filename
            except:
                return None

    def load_category_name(self, path):
        categoty_list = []
        if os.path.isfile(path):
            with open(path, 'r') as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    categoty_list.append(lines[i].strip('\n'))
        else:
            print("No existing categories!")
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> No existing categories!")
        if categoty_list:
            self.clear_category_area()
            self.show_category_name(categoty_list)
        else:
            print("Name file is empty!")

    def show_category_name(self, lst):
        name_no = len(lst)
        row_no = self.ui.tableWidget_categories.rowCount()
        for i in range(1, row_no):
            self.ui.tableWidget_categories.removeRow(i)
        for j in range(name_no):
            self.ui.tableWidget_categories.insertRow(j+1)
            self.ui.tableWidget_categories.setItem(j+1, 0, QTableWidgetItem())
            self.ui.tableWidget_categories.setItem(j+1, 1, QTableWidgetItem(lst[j]))
            self.ui.tableWidget_categories.setVerticalHeaderItem(j+1, QTableWidgetItem(str(j)))
    
    def save_category_name(self): 
        name_list = []
        row_no = self.ui.tableWidget_categories.rowCount()
        for i in range(row_no-1):
            name_list.append(self.ui.tableWidget_categories.item(i+1, 1).text())
        with open(self.category_name_file_path, 'w') as f:
            lines = []
            for j in range(len(name_list)):
                if j == len(name_list)-1:
                    lines.append(name_list[j])
                else:
                    lines.append(name_list[j] + '\n')
            for line in lines:
                f.write(line)
        self.show_info(self.ui.textEdit_statusBar,  self.category_name_file_path + "  Category name saved successfully!")

    def clear_history(self):
        """
        Clear the old data of last labeling.
        It is no necessary to reset all params, but I do so for safety's sake.
        """
        self.frame_index = 0
        self.real_frame_index = 0
        self.saved_rects = []
        self.unsaved_rects = []
        self.selected_rect = []
        self.selected_saved_rect_index = -1
        self.selected_unsaved_rect_index = -1
        self.current_category_index = -1
        self.current_category_id = -1
        self.current_category_name = ""
        self.category_color_dic = {}
        self.id_str = ""
        self.keep_loading = False
        self.frame_index = 0
        self.frame_step = 1 
        self.imgarea_width = 0
        self.imgarea_height = 0
        self.imgarea_pos = QPoint(0, 0)
        self.lefttop_corner = QPoint(0, 0)
        self.rightbottom_corner = QPoint(0, 0)
        self.cursor_pos = QPoint(0, 0)
        self.is_mouse_moving = False

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
            self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Close folder first!")
        #TODO: let user to decide weather to keep old data
        parent_dir = os.path.dirname(self.file_path)
        self.category_name_file_path = parent_dir + "/category.name"
        self.clear_category_area()
        self.load_category_name(self.category_name_file_path)
        self.clear_history()
        self.keep_labeling = True # set keep_labeling as False after finished labeling work
        while self.keep_labeling:
            self.open_cap()

    def open_cap(self):
        self.cap = cv2.VideoCapture(self.file_path)
        self.total_frames = self.cap.get(7)
        self.show_info(self.ui.label_totalFrames_2, str(int(self.total_frames)))
        self.num_digits = len(str(int(self.total_frames)))
        self.count = 0 #TODO: count should start from current frame index

        if self.ui.plainTextEdit_frameStep.toPlainText() != "":
            frame_step = self.ui.plainTextEdit_frameStep.toPlainText()
        else:
            frame_step = self.cap.get(5)
        frame_step = int(frame_step)

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
            self.show_info(self.ui.textEdit_statusBar, self.img_path + "<span style=\" color:#ff0000;\"> Error : Read wrong frame!")  
        else:
            self.show_info(self.ui.label_currentFrame_2, str(self.frame_index))
            print("Read correctly  Expect: " + str(self.frame_index) + " Real: " + str(int(self.real_frame_index))) 
        
        if ret == True:
            img_name = self.file_name + "_frame{}.jpg".format(str(self.frame_index).zfill(self.num_digits))
            label_name = self.file_name + "_frame{}.txt".format(str(self.frame_index).zfill(self.num_digits))
            self.img_path = os.path.join(self.file_path_without_ext, img_name).replace('\\', '/')
            self.label_path = os.path.join(self.file_path_without_ext, label_name).replace('\\', '/')
            if not os.path.isfile(self.label_path):
                f = open(self.label_path, "w")
                f.close()
            
            if os.path.isfile(self.img_path) == False:
                cv2.imwrite(self.img_path, cur_img) 

            self.setWindowTitle("Tagging:  " + self.img_path)
            self.raw_pixmap = QPixmap(self.img_path)
            #self.raw_pixmap_copy = self.raw_pixmap.copy()

            self.scale_img()
            self.calculate_bbox_pos()    
            self.draw_img()
    
    def read_image(self):
        self.total_frames = len(self.file_names)
        if self.frame_index < self.total_frames:
            cur_img_name = self.file_names[self.frame_index]
            self.img_path = os.path.join(self.file_dir, cur_img_name).replace('\\', '/')

            self.setWindowTitle("Tagging:  " + self.img_path)
            # TODO: change title to default at somewhere

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
        if self.is_mouse_moving == False:
            self.lefttop_corner = QPoint(0, 0)
            self.rightbottom_corner = QPoint(0, 0)

        self.calculate_bbox_ratio()
        self.save_bbox_ratio()

    def calculate_bbox_ratio(self):
        self.bbox_pos_x_ratio = self.bbox_pos_x / self.res_width
        self.bbox_pos_y_ratio = self.bbox_pos_y / self.res_height
        self.bbox_width_ratio = self.bbox_width / self.res_width
        self.bbox_height_ratio = self.bbox_height / self.res_height

    def save_bbox_ratio(self):
        if self.bbox_pos_x_ratio >= 0 and self.bbox_pos_y_ratio >= 0:
            lst = []
            _lst = []
            if self.current_category_id != -1:
                lst.append(self.current_category_id)
                print("current category: ", self.current_category_id)
            else:
                lst.append(-1) 
            _lst.append(self.bbox_pos_x_ratio)
            _lst.append(self.bbox_pos_y_ratio)
            _lst.append(self.bbox_width_ratio)
            _lst.append(self.bbox_height_ratio)
            lst.append(_lst)
            self.unsaved_rects.append(lst)
            self.newly_draw_rect_index = len(self.unsaved_rects) - 1   

    def draw_img(self):
        image = self.res_pixmap.copy()
        painter = QPainter(image)
        if not self.category_color_dic:
            self.category_color_dic = self.category_defaultcolor_dic

        defaultcolor_no = len(self.category_defaultcolor_dic)
        for i in range(defaultcolor_no - 1):            
            last_row = self.ui.tableWidget_categories.rowCount() - 1
            if i+1 <= last_row:
                item2 = self.ui.tableWidget_categories.item(i+1, 0)
                item2.setBackground(QBrush(self.category_defaultcolor_dic[i]))
            elif i+1 > last_row:
                self.add_category()
                item2 = self.ui.tableWidget_categories.item(i+1, 0)
                item2.setBackground(QBrush(self.category_defaultcolor_dic[i]))


        if self.saved_rects:
            for item in self.saved_rects:
                if item[0] < len(self.category_defaultcolor_dic) - 1:
                    painter.setPen(QPen(self.category_color_dic[int(item[0])], 2))
                else:
                    painter.setPen(QPen(self.category_color_dic[15], 2))   # TODO: Warn user to assign colors by himself.
                
                _bbox_pos_x = self.res_width * item[1][0]
                _bbox_pos_y = self.res_height * item[1][1] 
                _bbox_width = self.res_width * item[1][2]
                _bbox_height = self.res_height * item[1][3]
                self.rect = QRectF(_bbox_pos_x, _bbox_pos_y, _bbox_width, _bbox_height)
                painter.drawRect(self.rect)
                self.put_txt(item[0], painter)
        if self.unsaved_rects:
            for item in self.unsaved_rects:
                if int(item[0]) > -1:
                    painter.setPen(QPen(self.category_color_dic[int(item[0])], 1, Qt.DashDotDotLine))
                    _bbox_pos_x = self.res_width * item[1][0]
                    _bbox_pos_y = self.res_height * item[1][1]
                    _bbox_width = self.res_width * item[1][2]
                    _bbox_height = self.res_height * item[1][3]
                    self.rect = QRectF(_bbox_pos_x, _bbox_pos_y, _bbox_width, _bbox_height)
                    painter.drawRect(self.rect)
                    self.put_txt(item[0], painter)
                else:
                    self.show_info(self.ui.textEdit_statusBar, "<span style=\" color:#ff0000;\"> Choose a color first!")
                    # TODO: for now, if dont apply color, still draw rect
                    self.selected_rect = []
        if self.selected_rect:
            for item in self.selected_rect:
                painter.setPen(QPen(Qt.gray, 2, Qt.DotLine))
                _bbox_pos_x = self.res_width * item[1][0]
                _bbox_pos_y = self.res_height * item[1][1]
                _bbox_width = self.res_width * item[1][2]
                _bbox_height = self.res_height * item[1][3]
                self.rect = QRectF(_bbox_pos_x, _bbox_pos_y, _bbox_width, _bbox_height)
                painter.drawRect(self.rect)
                self.put_txt(item[0], painter)
        self.ui.img_area.setPixmap(image)
        painter.end()
    
    def put_txt(self, content, painter):
        if content != -1:
            bbox_text = "  " + str(content)
            painter.setFont(QFont("Arial", 15))
            painter.drawText(int(self.rect.x()), int(self.rect.y()), 40, 40, 1, bbox_text)
        else:
            painter.setFont(QFont("Arial", 15))
            painter.drawText(int(self.rect.x()), int(self.rect.y()), 40, 40, 1, "  ?")

    def unlock_loop(self):
        self.wait = False

    def set_frame_setting(self, flag):
        if flag == 0:
            self.ui.plainTextEdit_startFrame.setPlainText("0")
            self.ui.plainTextEdit_frameStep.setPlainText("1")
        else:
            self.ui.plainTextEdit_startFrame.setPlainText("N.A.")
            self.ui.plainTextEdit_frameStep.setPlainText("N.A.")
            self.ui.label_totalFrames_2.setText("N.A.")
            self.ui.label_currentFrame_2.setText("N.A.")

class SecWindow(QDialog):
    def __init__(self, parent = None):
        super(SecWindow, self).__init__(parent)
        #Load UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app_window = AppWindow()
    app_window.annotation_format = AnnotationYOLO()
    app_window.show()

    sys.exit(app.exec_())

