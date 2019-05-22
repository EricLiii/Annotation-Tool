
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

