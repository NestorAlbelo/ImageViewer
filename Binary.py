from Data import Data
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import PyQt5
import numpy as np
import os


class Binary(Data):
    def __init__(self, _parent, _filePath):
        super().__init__(_parent, _filePath)

        # Check data size for header calculation
        self.size = os.path.getsize(self.filePath)
        self.currentImageSize = 0

        self.createUI()
        self.updateHeadersLength()


    def loadData(self):
        self.fileOpen = open(self.filePath, "r")
        self.fileOpen.seek(int(self.headerLength.text()))

        self.width = int(self.imageWidth.text())
        self.height = int(self.imageHeight.text())
        self.frames = int(self.numberFrames.text())
        imageSize = self.width * self.height      

        # Load images in float if it's in complex
        if (self.complexImage.isChecked()):
            self.isComplex = True
            self.dataType = "float"
            self.bytesPerPixel = 4
            imageFormat = "f4"
            imageSize = imageSize * 2

            # Set dataset endianess.
            if (not self.littleEndian.isChecked()):
                imageFormat = '>'+imageFormat
            
            self.data = np.fromfile(self.fileOpen, dtype=imageFormat, count=((self.width * self.height * self.frames * 2))).reshape(self.frames, self.width, self.height, 2)

        # Load images like an integer.
        else:
            imageFormat = "i" + self.pixelWidth.text()
            self.bytesPerPixel = int(self.pixelWidth.text())

            # Set dataset endianess.
            if (not self.littleEndian.isChecked()):
                imageFormat = '>'+imageFormat

            self.data = np.fromfile(self.fileOpen, dtype=imageFormat, count=((self.width * self.height * self.frames))).reshape(self.frames, self.width, self.height)
            
    def createUI(self):
        
        # Labels
        # -------------------------------------------------------------------- #
        self.fileNameLabel = QLabel("File name:")
        if (len(self.filePath) > 48):
            self.fileName = QLabel("..." + self.filePath[-48:])
        else:
            self.fileName = QLabel(self.filePath)
        
        self.fileName.setToolTip(self.filePath)

        self.imageWidthLabel = QLabel("Image Width:")
        self.imageHeightLabel = QLabel("Image Height:")
        self.numberFramesLabel = QLabel("Number of Frames:")
        self.littleEndiaLabel = QLabel("Little Endian:")
        self.complexImageLabel = QLabel("Complex Image:")
        self.pixelWidthLabel = QLabel("Pixel Width:")
        self.headerLengthLabel = QLabel("Header Length:")
        # -------------------------------------------------------------------- #

        # Properties
        # -------------------------------------------------------------------- #
        boldFont=PyQt5.QtGui.QFont()
        boldFont.setBold(True)
        self.fileNameLabel.setFont(boldFont)
        self.imageWidthLabel.setFont(boldFont)
        self.imageHeightLabel.setFont(boldFont)
        self.numberFramesLabel.setFont(boldFont)
        self.littleEndiaLabel.setFont(boldFont)
        self.complexImageLabel.setFont(boldFont)
        self.pixelWidthLabel.setFont(boldFont)
        self.headerLengthLabel.setFont(boldFont)
        # -------------------------------------------------------------------- #

        # QLineEdit
        # -------------------------------------------------------------------- #
        self.imageWidth = QLineEdit("2048")
        self.imageHeight = QLineEdit("2048")
        self.numberFrames = QLineEdit("1")
        self.pixelWidth = QLineEdit("4")
        self.headerLength = QLineEdit("0")
        # -------------------------------------------------------------------- #

        # QCheckBox
        # -------------------------------------------------------------------- #
        self.littleEndian = QCheckBox()
        self.complexImage = QCheckBox()
        # -------------------------------------------------------------------- #

        # Connect events
        # -------------------------------------------------------------------- #
        self.imageWidth.textChanged.connect(self.updateHeadersLength)
        self.imageHeight.textChanged.connect(self.updateHeadersLength)
        self.numberFrames.textChanged.connect(self.updateHeadersLength)
        self.pixelWidth.textChanged.connect(self.updateHeadersLength)
        self.complexImage.toggled.connect(self.updateHeadersLength)
        # -------------------------------------------------------------------- #

        # Insert UI in array
        self.ui = [
            [self.fileNameLabel, 0, 0, 1, 1],
            [self.fileName, 0, 1, 1, 1],
            [self.imageWidthLabel, 1, 0, 1, 1],
            [self.imageWidth, 1, 1, 1, 1],
            [self.imageHeightLabel, 2, 0, 1, 1],
            [self.imageHeight, 2, 1, 1, 1],
            [self.numberFramesLabel, 3, 0, 1, 1],
            [self.numberFrames, 3, 1, 1, 1],
            [self.littleEndiaLabel, 4, 0, 1, 1],
            [self.littleEndian, 4, 1, 1, 1],
            [self.complexImageLabel, 5, 0, 1, 1],
            [self.complexImage, 5, 1, 1, 1],
            [self.pixelWidthLabel, 6, 0, 1, 1],
            [self.pixelWidth, 6, 1, 1, 1],
            [self.headerLengthLabel, 7, 0, 1, 1],
            [self.headerLength, 7, 1, 1, 1],
        ]

    def updateHeadersLength(self):
        # Fill header length with expected size based on current dimensions
        try: 
            self.currentImageSize = int(self.imageWidth.text()) * int(self.imageHeight.text()) * int(self.numberFrames.text()) * int(self.pixelWidth.text())
        except:
            self.currentImageSize = 0

        # If the image is complex there are numberFrames * 2
        if(self.complexImage.isChecked()):
            self.currentImageSize = self.currentImageSize * 2

        # Input file Header
        if (self.currentImageSize > self.size):
            self.headerLength.setStyleSheet("color: red;")
        else:
            self.headerLength.setStyleSheet("")

        self.headerLength.setText(str(self.size - self.currentImageSize))