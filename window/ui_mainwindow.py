
#(testqt) D:\MyWork\Tools\Annotation_Tool\window>python D:\Software\Anaconda\envs\testqt\Library\bin\pyside2-uic mainwindow.ui 
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Fri May 17 14:57:26 2019
#      by: pyside2-uic 2.0.0 running on PySide2 5.6.0~a1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1020, 842)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.img_area = QtWidgets.QLabel(self.centralWidget)
        self.img_area.setEnabled(True)
        self.img_area.setMinimumSize(QtCore.QSize(1002, 587))
        self.img_area.setFrameShape(QtWidgets.QFrame.Box)
        self.img_area.setText("")
        self.img_area.setObjectName("img_area")
        self.verticalLayout_2.addWidget(self.img_area)
        self.btn_area = QtWidgets.QGroupBox(self.centralWidget)
        self.btn_area.setMinimumSize(QtCore.QSize(1002, 100))
        self.btn_area.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btn_area.setTitle("")
        self.btn_area.setObjectName("btn_area")
        self.btn_next = QtWidgets.QPushButton(self.btn_area)
        self.btn_next.setGeometry(QtCore.QRect(200, 40, 75, 23))
        self.btn_next.setObjectName("btn_next")
        self.btn_prev = QtWidgets.QPushButton(self.btn_area)
        self.btn_prev.setGeometry(QtCore.QRect(40, 40, 75, 23))
        self.btn_prev.setObjectName("btn_prev")
        self.btn_save = QtWidgets.QPushButton(self.btn_area)
        self.btn_save.setGeometry(QtCore.QRect(540, 40, 75, 23))
        self.btn_save.setObjectName("btn_save")
        self.btn_clear = QtWidgets.QPushButton(self.btn_area)
        self.btn_clear.setGeometry(QtCore.QRect(780, 40, 75, 23))
        self.btn_clear.setObjectName("btn_clear")
        self.btn_delete = QtWidgets.QPushButton(self.btn_area)
        self.btn_delete.setGeometry(QtCore.QRect(660, 40, 75, 23))
        self.btn_delete.setObjectName("btn_delete")
        self.label_fps = QtWidgets.QLabel(self.btn_area)
        self.label_fps.setGeometry(QtCore.QRect(340, 30, 41, 31))
        self.label_fps.setObjectName("label_fps")
        self.textedit_fps = QtWidgets.QTextEdit(self.btn_area)
        self.textedit_fps.setGeometry(QtCore.QRect(390, 30, 51, 31))
        self.textedit_fps.setObjectName("textedit_fps")
        self.verticalLayout_2.addWidget(self.btn_area)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1020, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuLabeling_for_Yolo = QtWidgets.QMenu(self.menuBar)
        self.menuLabeling_for_Yolo.setGeometry(QtCore.QRect(0, 100, 140, 94))
        self.menuLabeling_for_Yolo.setObjectName("menuLabeling_for_Yolo")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.act_openfile = QtWidgets.QAction(MainWindow)
        self.act_openfile.setObjectName("act_openfile")
        self.act_opendir = QtWidgets.QAction(MainWindow)
        self.act_opendir.setObjectName("act_opendir")
        self.actions = QtWidgets.QAction(MainWindow)
        self.actions.setObjectName("actions")
        self.menuLabeling_for_Yolo.addAction(self.act_openfile)
        self.menuLabeling_for_Yolo.addAction(self.act_opendir)
        self.menuBar.addAction(self.menuLabeling_for_Yolo.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.btn_next.setText(QtWidgets.QApplication.translate("MainWindow", "Next", None, -1))
        self.btn_prev.setText(QtWidgets.QApplication.translate("MainWindow", "Back", None, -1))
        self.btn_save.setText(QtWidgets.QApplication.translate("MainWindow", "Save", None, -1))
        self.btn_clear.setText(QtWidgets.QApplication.translate("MainWindow", "Clear all", None, -1))
        self.btn_delete.setText(QtWidgets.QApplication.translate("MainWindow", "Delete", None, -1))
        self.label_fps.setText(QtWidgets.QApplication.translate("MainWindow", "FPS", None, -1))
        self.menuLabeling_for_Yolo.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.act_openfile.setText(QtWidgets.QApplication.translate("MainWindow", "Open file", None, -1))
        self.act_opendir.setText(QtWidgets.QApplication.translate("MainWindow", "Open Directory", None, -1))
        self.actions.setText(QtWidgets.QApplication.translate("MainWindow", "s", None, -1))

