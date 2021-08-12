from numpy.lib.type_check import iscomplex
from ImageData import ImageData
from ShowMeta import ShowMeta
from Fits import Fits
from Binary import Binary
from Alert import Alert
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from astropy.io import fits
import PyQt5
import astropy
import numpy as np
import os

class LoadData(QDialog):
    def __init__(self, _mainReference, _filePath):
        super(LoadData, self).__init__()
        self.mainReference = _mainReference

        self.fullPathMainData = _filePath
        self.fullPathCompareData = ""

        self.imageDataInstances = []

        self.mainData = 0
        self.compareData = None

        self.createUI()

    def loadFileToCompare(self):
        self.fullPathCompareData = QFileDialog.getOpenFileName(self, "Open Compare File", self.mainReference.getWorkingDirectory())[0]
        
        if (self.fullPathCompareData):
            self.mainReference.setWorkingDirectory(self.fullPathCompareData)

            if (self.fullPathCompareData.endswith(".fits")):
                self.compareData = Fits(self, self.fullPathCompareData)
            else:
                self.compareData = Binary(self, self.fullPathCompareData)    

            for ui in self.compareData.ui:
                self.panelLayout.addWidget(ui[0], self.positionCompareUI + ui[1], ui[2], ui[3], ui[4])   

            self.loadFileToCompareButton.setEnabled(False)


    def showImage(self):

        # Check maindata file dimensions if necessary
        if (self.mainData.isBinary):
            mainHeaderLength = int(self.mainData.headerLength.text())
            if ((mainHeaderLength < 0) or ((mainHeaderLength + self.mainData.currentImageSize) > self.mainData.size)):
                self.alert = Alert("Error. Please check dimensions of the main data.")
                self.alert.show()
                return

        # Load mainData
        self.mainData.loadData()

        if (self.compareData):
            
            # Is Binary
            if (self.compareData.isBinary):
                compareHeaderLength = int(self.headerLengthCompare.text())
                if ((compareHeaderLength < 0) or ((compareHeaderLength + self.compareData.currentImageSize) > self.compareData.size)):
                    self.alert = Alert("Error. Please check dimensions of the compare data.")
                    self.alert.show()
                    return
                
                if ((self.mainData.width != int(self.compareData.imageWidth.text())) or
                    (self.mainData.height != int(self.compareData.imageHeight.text())) or
                    (self.mainData.frames > int(self.compareData.numberFrames.text())) or 
                    (self.mainData.isComplex != self.compareData.isComplex)):
                    self.alert = Alert("Error. Please check dimensions of the compare data. These must be equal to the input image")
                    self.alert.show()
                    return

            # Is Fits
            else:
                # Compare dimensions with main data
                if ((self.mainData.width != self.compareData.width) or
                    (self.mainData.height != self.compareData.height) or
                    (self.mainData.frames > self.compareData.frames) or 
                    (self.mainData.isComplex)):
                    self.alert = Alert("Error. Please check dimensions of the compare data. These must be equal to the input image")
                    self.alert.show()
                    return

            # Load compare data
            self.compareData.loadData()

        self.imageDataInstances.append(ImageData(self, self.mainData, self.compareData))
        self.imageDataInstances[-1].show()

    def createUI(self):

        self.setWindowTitle("Load Data")

        # Buttons
        # -------------------------------------------------------------------- #
        self.loadFileToCompareButton = QPushButton("Load file to compare")
        self.showImageButton = QPushButton("Show Image")
        # -------------------------------------------------------------------- #
    
        # Events
        # -------------------------------------------------------------------- #
        self.loadFileToCompareButton.clicked.connect(self.loadFileToCompare)
        self.showImageButton.clicked.connect(self.showImage)
        # -------------------------------------------------------------------- #

        # Layouts
        # -------------------------------------------------------------------- #
        self.panelLayout = QGridLayout()
        # -------------------------------------------------------------------- #

        if (self.fullPathMainData.endswith(".fits")):
            self.mainData = Fits(self, self.fullPathMainData)
        else:
            self.mainData = Binary(self, self.fullPathMainData)

        # Insert UI in panel
        for ui in self.mainData.ui:
            self.panelLayout.addWidget(ui[0], ui[1], ui[2], ui[3], ui[4])

        self.panelLayout.addWidget(self.loadFileToCompareButton, len(self.mainData.ui), 0, 1, 1)
        self.panelLayout.addWidget(self.showImageButton, 200, 0, 1, 1)
        #verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        #self.panelLayout.addItem(verticalSpacer)

        self.positionCompareUI = len(self.mainData.ui) + 1

        self.setLayout(self.panelLayout)

    def loadCompareData(self):
        print("Loading Compare data")