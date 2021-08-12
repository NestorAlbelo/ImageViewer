from Data import Data
from ShowMeta import ShowMeta
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import PyQt5
from astropy.io import fits
import astropy
import numpy as np
import os

class Fits(Data):
    def __init__(self, _parent, _filePath):
        super().__init__(_parent, _filePath)

        # Check data size for header calculation
        self.size = os.path.getsize(self.filePath)
        self.isBinary = False
        self.metaWindows = []

        # Open Fits file
        self.fileOpen = fits.open(self.filePath)

        header = self.fileOpen[0].header
        self.width = int(header["NAXIS1"])
        self.height = int(header["NAXIS2"])

        if (header["NAXIS"] == 3):
            self.frames = int(header["NAXIS3"])
        else:
            self.frames = 1

        if (header["BITPIX"] == 16):
            self.bytesPerPixel = 2
        elif (header["BITPIX"] == 32):
            self.bytesPerPixel = 4

        self.createUI()

    def loadData(self):
        self.data = self.fileOpen[0].data

    def createUI(self):
        
        # Labels
        # -------------------------------------------------------------------- #
        self.fileNameLabel = QLabel("File name:")
        if (len(self.filePath) > 64):
            self.fileName = QLabel("..." + self.filePath[-64:])
        else:
            self.fileName = QLabel(self.filePath)
        
        self.fileName.setToolTip(self.filePath)
        
        self.metadataLabel = QLabel("Metadata")

        # Metadata Labels
        self.metaNameLabel = QLabel("Name")
        self.metaTypeLabel = QLabel("Type")
        self.metaDimensionsLabel = QLabel("Dimensions")
        self.metaViewLabel = QLabel("View")

        # -------------------------------------------------------------------- #

        # Properties
        # -------------------------------------------------------------------- #
        boldFont=PyQt5.QtGui.QFont()
        boldFont.setBold(True)
        self.fileNameLabel.setFont(boldFont)
        self.metadataLabel.setFont(boldFont)
        self.metaNameLabel.setFont(boldFont)
        self.metaTypeLabel.setFont(boldFont)
        self.metaDimensionsLabel.setFont(boldFont)
        self.metaViewLabel.setFont(boldFont)
        self.metaViewLabel.setAlignment(Qt.AlignCenter)
        # -------------------------------------------------------------------- #

        # Buttons
        # -------------------------------------------------------------------- #
        self.buttonsMetadata = []
        # -------------------------------------------------------------------- #

        # Insert UI in array
        self.ui = [
            [self.fileNameLabel, 0, 0, 1, 1],
            [self.fileName, 0, 1, 1, 4],
            [self.metadataLabel, 1, 0, 1, 1],
            [self.metaNameLabel, 2, 0, 1, 1],
            [self.metaTypeLabel, 2, 1, 1, 1],
            [self.metaDimensionsLabel, 2, 2, 1, 1],
            [self.metaViewLabel, 2, 3, 1, 2]
        ]

        baseIndex = 3
        for index, meta in enumerate(self.fileOpen):
            if (isinstance(meta, astropy.io.fits.hdu.image.PrimaryHDU)):
                # Create and Add Labels
                self.ui.append([QLabel("PRIMARY"), baseIndex + index, 0, 1, 1])
                self.ui.append([QLabel("Image"), baseIndex + index, 1, 1, 1])
                self.ui.append([QLabel(str(self.fileOpen[index].data.shape)), baseIndex + index, 2, 1, 1])

                # Create and Add Buttons
                self.buttonsMetadata.append(QPushButton("Header"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, True))(index))
                self.ui.append([self.buttonsMetadata[-1], baseIndex + index, 3, 1, 2])


            elif (isinstance(meta, astropy.io.fits.hdu.image.ImageHDU)):
                # Create and Add Labels
                self.ui.append([QLabel(str(self.fileOpen[index].name)), baseIndex + index, 0, 1, 1])
                self.ui.append([QLabel("Image"), baseIndex + index, 1, 1, 1])
                self.ui.append([QLabel(f"({len(self.fileOpen[index].data)})"), baseIndex + index, 2, 1, 1])

                # Create and Add Buttons
                self.buttonsMetadata.append(QPushButton("Header"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, True))(index))
                self.ui.append([self.buttonsMetadata[-1], baseIndex + index, 3, 1, 1])
                
                self.buttonsMetadata.append(QPushButton("Plot"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, False))(index))
                self.ui.append([self.buttonsMetadata[-1], baseIndex + index, 4, 1, 1])

            elif (isinstance(meta, astropy.io.fits.hdu.table.TableHDU)):
                # Create and Add Labels
                self.ui.append([QLabel(str(self.fileOpen[index].name)), baseIndex + index, 0, 1, 1])
                self.ui.append([QLabel("ASCII"), baseIndex + index, 1, 1, 1])
                self.ui.append([QLabel(f"({len(self.fileOpen[index].data[0])},{self.fileOpen[index].data.shape[0]})"), baseIndex + index, 2, 1, 1])

                # Create and Add Buttons
                self.buttonsMetadata.append(QPushButton("Header"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, True))(index))
                self.ui.append([self.buttonsMetadata[-1], baseIndex + index, 3, 1, 1])
                
                self.buttonsMetadata.append(QPushButton("Plot"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, False))(index))
                self.ui.append([self.buttonsMetadata[-1], baseIndex + index, 4, 1, 1])
            else:
                print("Type not recognized")

    def showMetadata(self, indexMeta, isHeader):
        self.metaWindows.append(ShowMeta(self.parent, self.fileOpen[indexMeta], isHeader))
        self.metaWindows[-1].show()
