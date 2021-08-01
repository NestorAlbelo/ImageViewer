from ImageData import ImageData
from Alert import Alert
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QWidget
from PyQt5.uic import loadUi
from astropy.io import fits
import numpy as np
import os

class LoadFits(QDialog):
    def __init__(self, _mainReference, _filename):
        super(LoadFits, self).__init__()
        loadUi("GUIs/LoadFits.ui", self)
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

        self.showDataButton.clicked.connect(self.createImageData)

    def createImageData(self):

        # Check compare file dimensions
        if ((self.fullFilePathCompare != "") and ((int(self.headerLengthCompare.text()) < 0) or ((int(self.headerLengthCompare.text()) + self.currentImageSize) > self.fileSizeCompare))):
            self.alert = Alert("Error. Please check dimensions of the compare image. These must be equal to the input image and the header must not exceed the file size.")
            self.alert.show()

        else:        
            hdul = fits.open(self.fullFilePath)

            dataInput = hdul[0].data

            numberFrames, sizeX, sizeY = dataInput.shape

            dataCompare = None

            # Update UI
            #TODO: MOVE UP!!
            self.frames.setText(str(numberFrames))
            self.imageWidth.setText(str(sizeY))
            self.imageHeight.setText(str(sizeX))

            # TODO: CHECK LITTLE ENDIANESS & EXTRACT IMAGE FORMAT
            self.imageData.append(ImageData(self, dataInput, 
                                            self.fullFilePath.split('/')[-1], 
                                            sizeX, sizeY, numberFrames, "i", 
                                            False, False, dataCompare, 
                                            self.fullFilePathCompare.split('/')[-1]))
            self.imageData[-1].show()

