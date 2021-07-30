from ImageData import ImageData
from Alert import Alert
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QWidget
from PyQt5.uic import loadUi
import numpy as np
import os

class LoadBinary(QDialog):
    def __init__(self, _mainReference, _filename):
        super(LoadBinary, self).__init__()
        loadUi("GUIs/LoadBinary.ui", self)
        self.mainReference = _mainReference

        self.imageData = []

        self.filename.setToolTip(_filename)

        # Create label for fileName
        if len(_filename) > 32:
            filename = "..." + _filename[-32:]
        else:
            filename = _filename

        self.filename.setText(filename)
        self.fullFilePath = _filename
        self.fullFilePathCompare = ""
        self.fileSize = os.path.getsize(self.fullFilePath)
        self.fileSizeCompare = -1

        self.updateHeadersLength()

        # Events
        self.showDataButton.clicked.connect(self.createImageData)
        self.imageWidth.textChanged.connect(self.updateHeadersLength)
        self.imageHeight.textChanged.connect(self.updateHeadersLength)
        self.frames.textChanged.connect(self.updateHeadersLength)
        self.pixelWidth.textChanged.connect(self.updateHeadersLength)
        self.isComplexImage.toggled.connect(self.updateHeadersLength)   

        self.loadCompareImageButton.clicked.connect(self.loadCompareImage)


    def closeEvent(self, event):
        print("Closing LoadBinary window")
             
    def createImageData(self):

        # Check input file dimensions
        if ((int(self.headerLength.text()) < 0) or ((int(self.headerLength.text()) + self.currentImageSize) > self.fileSize)):
            self.alert = Alert("Error. Please check dimensions of the input image.")
            self.alert.show()

        # Check compare file dimensions
        elif ((self.fullFilePathCompare != "") and ((int(self.headerLengthCompare.text()) < 0) or ((int(self.headerLengthCompare.text()) + self.currentImageSize) > self.fileSizeCompare))):
            self.alert = Alert("Error. Please check dimensions of the compare image. These must be equal to the input image and the header must not exceed the file size.")
            self.alert.show()

        else:        
            fileInput = open(self.fullFilePath, "r")
            fileInput.seek(int(self.headerLength.text()))

            dataCompare = None
            fileCompare = None

            # Load Compare file if necessary
            if (self.fullFilePathCompare != ""):
                fileCompare = open(self.fullFilePathCompare, "r")
                fileCompare.seek(int(self.headerLengthCompare.text()))

            sizeX = int(self.imageWidth.text())
            sizeY = int(self.imageHeight.text())
            frames = int(self.frames.text())
            imageSize = sizeX * sizeY

            # Load images in float if it's in complex
            if (self.isComplexImage.isChecked()):
                imageFormat = "f4"
                imageSize = imageSize * 2

                # Set dataset endianess.
                if (not self.isLittleEndian.isChecked()):
                    imageFormat = '>'+imageFormat
                
                dataInput = np.fromfile(fileInput, dtype=imageFormat, count=((sizeX * sizeY * frames * 2))).reshape(frames, sizeX, sizeY, 2)

                if (self.fullFilePathCompare != ""):
                    dataCompare = np.fromfile(fileCompare, dtype=imageFormat, count=((sizeX * sizeY * frames * 2))).reshape(frames, sizeX, sizeY, 2)

            # Load images like an integer.
            else:
                imageFormat = "i" + self.pixelWidth.text()

                # Set dataset endianess.
                if (not self.isLittleEndian.isChecked()):
                    imageFormat = '>'+imageFormat

                dataInput = np.fromfile(fileInput, dtype=imageFormat, count=((sizeX * sizeY * frames))).reshape(frames, sizeX, sizeY)
                
                if (self.fullFilePathCompare != ""):
                    dataCompare = np.fromfile(fileCompare, dtype=imageFormat, count=((sizeX * sizeY * frames))).reshape(frames, sizeX, sizeY)

            self.imageData.append(ImageData(self, dataInput, 
                                            self.fullFilePath.split('/')[-1], 
                                            sizeX, sizeY, frames, imageFormat, 
                                            self.isComplexImage.isChecked(), 
                                            False, self.fullFilePath, 
                                            dataCompare, 
                                            self.fullFilePathCompare.split('/')[-1]))
            self.imageData[-1].move(100, 200)
            self.imageData[-1].show()

    def updateHeadersLength(self):    
        # Fill header length with expected size based on current dimensions
        self.currentImageSize = int(self.imageWidth.text()) * int(self.imageHeight.text()) * int(self.frames.text()) * int(self.pixelWidth.text())
        
        # If the image is complex there are Frames * 2
        if(self.isComplexImage.isChecked()):
            self.currentImageSize = self.currentImageSize * 2

        # Input file Header
        if (self.currentImageSize > self.fileSize):
            self.headerLength.setStyleSheet("color: red;")
        else:
            self.headerLength.setStyleSheet("")

        self.headerLength.setText(str(self.fileSize - self.currentImageSize))

        # Compare file Header
        if (self.filenameCompare.text() != ""):
            if (self.currentImageSize > self.fileSizeCompare):
                self.headerLengthCompare.setStyleSheet("color: red;")
            else:
                self.headerLengthCompare.setStyleSheet("")

            self.headerLengthCompare.setText(str(self.fileSizeCompare - self.currentImageSize))

    def loadCompareImage(self):
        filePath = QFileDialog.getOpenFileName(self, "Open File", self.mainReference.getWorkingDirectory())[0]
        self.mainReference.setWorkingDirectory(filePath)
        
        if (filePath != ""):
            if (filePath.endswith(".bin") or filePath.endswith(".phi")):
                self.labelFileNameCompare.setEnabled(True)
                self.filenameCompare.setEnabled(True)
                self.labelHeaderCompare.setEnabled(True)
                self.headerLengthCompare.setEnabled(True)

                self.fullFilePathCompare = filePath

                # Create label for filePath
                if len(filePath) > 35:
                    filePath = "..." + filePath[-35:]

                self.filenameCompare.setText(filePath)
                self.fileSizeCompare = os.path.getsize(self.fullFilePathCompare)

            else:
                self.alert = Alert("Error. The file is extension is not supported. Please use '.phi' or '.bin' files.")
                self.alert.show()

                self.labelFileNameCompare.setEnabled(False)
                self.filenameCompare.setEnabled(False)
                self.labelHeaderCompare.setEnabled(False)
                self.headerLengthCompare.setEnabled(False)

                self.fullFilePathCompare = ""
                self.filenameCompare.setText("")
                self.headerLengthCompare.setText("0")
                self.fileSizeCompare = -1
                
            self.filenameCompare.setToolTip(self.fullFilePathCompare)
            self.updateHeadersLength()