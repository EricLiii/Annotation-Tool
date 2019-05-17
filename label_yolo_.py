# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 2019

@author: Zefeng

Create & modify annotation(for yolo)
"""

import os
import cv2

class DatasetVerifier():
    def __init__(self):
        #self.WindowName = 'Image'
        self.ExistingRects = []
        self.FirstCorner = None
        self.SecondCorner = None
        
        #cv2.namedWindow(self.WindowName)
        
        #cv2.setMouseCallback(self.WindowName, self.onMouseClicked, 0)
    
    def verifyDataset(self, folderPath, resizeRatio):
    
        if os.path.isdir(folderPath) == False:
            print('Folder not found: {0}'.format(folderPath))
            return
        
        self.FolderPath = folderPath
        self.ResizeRatio = resizeRatio
        
        fileNames = []
        for filename in os.listdir(folderPath):
            txt_name = os.path.splitext(filename)[0]+".txt"
            #TODO: check file exists or not first 
            txt_path = os.path.join(self.FolderPath, txt_name).replace('\\', '/')
            print(txt_path)
            txt_file = open(txt_path, "w")
            txt_file.close()
            file_path = os.path.join(self.FolderPath, filename).replace('\\', '/')
            fileNames.append(txt_name)
        
        fileIndex = 0
        key = 0
        
        while (True):
            if key & 0xFF != ord('s'): # Don't read a new frame while saving label
                self.LabelFileName = fileNames[fileIndex]
            
                # Display image
                imageFilePath = '{0}/{1}.jpg'.format(folderPath, os.path.splitext(fileNames[fileIndex])[0])
                img = cv2.imread(imageFilePath)
                self.ImgHeight, self.ImgWidth, imgChannels = img.shape
                self.ResizedImg = cv2.resize(img, None, fx = resizeRatio, fy = resizeRatio)
            
            self.drawRectsAndDisplay()
            
            key = cv2.waitKey(0)
            
            if key & 0xFF == ord('n'): # Next image
                fileIndex = min(fileIndex + 1, len(fileNames) - 1)
            elif key & 0xFF == ord('b'): # Back to previous image
                fileIndex = max(fileIndex - 1, 0)
            elif key & 0xFF == ord('s'): # Save info to label file
                labelFilePath = '{0}/{1}'.format(self.FolderPath, self.LabelFileName)
                self.saveLabel(labelFilePath)
            elif key == 27: # ESC
                break
        
        cv2.destroyAllWindows()
        
    def saveLabel(self, savedFilePath):
        #calculate the rectangle coordinates in original size
        xMin = min(self.FirstCorner[0], self.SecondCorner[0])
        yMin = min(self.FirstCorner[1], self.SecondCorner[1])
        xMax = max(self.FirstCorner[0], self.SecondCorner[0])
        yMax = max(self.FirstCorner[1], self.SecondCorner[1])
        
        xCenter = float((xMin + xMax) / 2.0)
        yCenter = float((yMin + yMax) / 2.0)
        width = xMax - xMin
        height = yMax - yMin
        
        xCenterRatio = xCenter / self.ResizeRatio / self.ImgWidth
        yCenterRatio = yCenter / self.ResizeRatio / self.ImgHeight
        widthRatio = width / self.ResizeRatio / self.ImgWidth
        heightRatio = height / self.ResizeRatio / self.ImgHeight
        
        with open(savedFilePath, 'at') as fo:
            #TODO: let user to input the number of classes
            fo.write('1 {0} {1} {2} {3}\n'.format(xCenterRatio, yCenterRatio, widthRatio, heightRatio))
        
        self.resetDrawing()
        
    def drawRectsAndDisplay(self):
        image = self.ResizedImg.copy()
        
        cv2.putText(image, self.LabelFileName, (300, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            
        # Read label and rects
        labelFilePath = '{0}/{1}'.format(self.FolderPath, self.LabelFileName)
        with open(labelFilePath, 'rt') as fi:
            self.ExistingRects = []
            for line in fi:
                if line != '\n':
                    originalRectRatios = line.split()[1:]
                    
                    xCenter = self.ImgWidth * float(originalRectRatios[0]) * self.ResizeRatio
                    yCenter = self.ImgHeight * float(originalRectRatios[1]) * self.ResizeRatio
                    width = self.ImgWidth * float(originalRectRatios[2]) * self.ResizeRatio
                    height = self.ImgHeight * float(originalRectRatios[3]) * self.ResizeRatio
                    
                    firstCorner = (int(xCenter - width/2), int(yCenter - height/2))
                    secondCorner = (int(xCenter + width/2), int(yCenter + height/2))
                    
                    self.ExistingRects.append((firstCorner, secondCorner))
        
        for rect in self.ExistingRects:
            cv2.rectangle(image, rect[0], rect[1], (255, 0, 0), 2)
            
        if (not self.FirstCorner is None) and (not self.SecondCorner is None):
            cv2.rectangle(image, self.FirstCorner, self.SecondCorner, (0, 0, 255))
        
        # Show everything
        #cv2.imshow(self.WindowName, image)
        #return image
     
    '''
    Check if the input point in inside a rect. Delete if found.
    Return the index of the rect if found, otherwise -1.
    '''
    def deleteSelectedExistingRects(self, point):
        
        for i in range(0, len(self.ExistingRects)):
            rect = self.ExistingRects[i]
        
            if (rect[0][0] < point[0] and point[0] < rect[1][0] and
                rect[0][1] < point[1] and point[1] < rect[1][1]):
                
                labelFilePath = '{0}{1}'.format(self.FolderPath, self.LabelFileName)
                
                with open(labelFilePath, 'rt') as fi:
                    lines = fi.readlines()
                    
                del lines[i]
                with open(labelFilePath, 'wt') as fo:
                    fo.writelines(lines)
        
                return i
        
        return -1
    
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
    
    def resetDrawing(self):
        self.FirstCorner = None
        self.SecondCorner = None
        
if __name__ == '__main__':
    
    print('How to use:\n\
          \'n\' for the next frame.\n\
          \'s\' to save the label file and rectangles.\n\
          Saved rects appear in blue.\n\
          Newly drawn (haven not been saved) rects appear in red.\n\
          Press, drag and release the left mouse button to draw a new rectangle (appear in red).\n\
          Right click inside a blue rectangle (saved rectangle) to delete it.\n\
          Right click anywhere else to delete the newly drawn (haven not been saved) rectangle.\n'
          )
    
    datasetFolderPath = 'd:/dangdang/DataDNN/ShipSmoke/yolo_dataset/ManuallyCropped/psa_20190218_162533_183'
    resizeRatio = 2 # From original -> display
    
    verifier = DatasetVerifier()
    verifier.verifyDataset(datasetFolderPath, 1.0 / resizeRatio)