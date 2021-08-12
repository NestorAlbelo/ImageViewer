from ImageData import ImageData
from ShowMeta import ShowMeta
from Alert import Alert
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from astropy.io import fits
import astropy
import numpy as np
import os

class LoadFits(QDialog):
    def __init__(self, _mainReference, _filename):
        super(LoadFits, self).__init__()
        #loadUi("GUIs/LoadFits.ui", self)
        self.mainReference = _mainReference

        self.imageData = []

        self.fullFilePath = _filename
        self.fullFilePathCompare = ""
        self.frames = 1
        self.sizeX = 0
        self.sizeY = 0
        
        # Open Fits file
        self.hdul = fits.open(self.fullFilePath)

        self.createUI(_filename)

    def createImageData(self):

        # Check compare file dimensions
        if ((self.fullFilePathCompare != "") and ((int(self.headerLengthCompare.text()) < 0) or ((int(self.headerLengthCompare.text()) + self.currentImageSize) > self.fileSizeCompare))):
            self.alert = Alert("Error. Please check dimensions of the compare image. These must be equal to the input image and the header must not exceed the file size.")
            self.alert.show()

        else:        
            dataInput = self.hdul[0].data

            header = self.hdul[0].header
            self.sizeX = int(header["NAXIS1"])
            self.sizeY = int(header["NAXIS2"])

            if (header["NAXIS"] > 2):
                self.frames = int(header["NAXIS3"])

            dataCompare = None

            # TODO: CHECK LITTLE ENDIANESS & EXTRACT IMAGE FORMAT
            self.imageData.append(ImageData(self, dataInput, 
                                            self.fullFilePath.split('/')[-1], 
                                            self.sizeX, self.sizeY, self.frames, "i", 
                                            False, False, dataCompare, 
                                            self.fullFilePathCompare.split('/')[-1]))
            self.imageData[-1].show()

    def createUI(self, _filename):

        # Labels
        # -------------------------------------------------------------------- #
        self.labelFileName = QLabel("File name:")
        self.filename = QLabel("")
        self.labelMetadata = QLabel("Metadata")
        self.labelFileNameCompare = QLabel("File name compare:")
        self.filenameCompare = QLabel("")
        self.labelsMetadata = []
        self.labelsMetadataCompare = []
        # -------------------------------------------------------------------- #

        # Properties
        # -------------------------------------------------------------------- #
        boldFont=PyQt5.QtGui.QFont()
        boldFont.setBold(True)
        self.labelFileName.setFont(boldFont)
        self.labelMetadata.setFont(boldFont)
        self.labelFileNameCompare.setFont(boldFont)
        # -------------------------------------------------------------------- #

        # Buttons
        # -------------------------------------------------------------------- #
        self.loadCompareImageButton = QPushButton("File To Compare")
        self.showDataButton = QPushButton("Show Image")
        self.buttonsMetadata = []
        self.buttonsMetadataCompare = []
        # -------------------------------------------------------------------- #

        # Connect events
        # -------------------------------------------------------------------- #
        self.showDataButton.clicked.connect(self.createImageData)
        # -------------------------------------------------------------------- #

        # Canvas
        # -------------------------------------------------------------------- #
        self.main_layoutImageData = QGridLayout()
        self.panelLayout = QGridLayout()
        # -------------------------------------------------------------------- #

        # Add Widgets
        # -------------------------------------------------------------------- #
        # Panel
        self.panelLayout.addWidget(self.labelFileName, 0, 0)
        self.panelLayout.addWidget(self.filename, 0, 1, 1, 4)

        self.panelLayout.addWidget(self.labelMetadata, 1, 0)
        # Division for metadata
        # print(len(self.hdul[6].data[65]))

        viewLabel = QLabel("View")
        viewLabel.setAlignment(Qt.AlignCenter)

        self.panelLayout.addWidget(QLabel("Name"), 2, 0)
        self.panelLayout.addWidget(QLabel("Type"), 2, 1)
        self.panelLayout.addWidget(QLabel("Dimensions"), 2, 2)
        self.panelLayout.addWidget(viewLabel, 2, 3, 1, 2)

        baseIndex = 3

        for index, meta in enumerate(self.hdul):
            if (isinstance(meta, astropy.io.fits.hdu.image.PrimaryHDU)):
                # Create and Add Labels
                self.labelsMetadata.append(QLabel("PRIMARY"))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 0)

                self.labelsMetadata.append(QLabel("Image"))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 1)

                self.labelsMetadata.append(QLabel(str(self.hdul[index].data.shape)))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 2)
                # Create and Add Buttons
                self.buttonsMetadata.append(QPushButton("Header"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, True))(index))
                self.panelLayout.addWidget(self.buttonsMetadata[-1], baseIndex + index, 3)

            elif (isinstance(meta, astropy.io.fits.hdu.image.ImageHDU)):
                # Create and Add Labels
                self.labelsMetadata.append(QLabel(str(self.hdul[index].name)))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 0)

                self.labelsMetadata.append(QLabel("Image"))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 1)

                self.labelsMetadata.append(QLabel(f"({len(self.hdul[index].data)})"))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 2)

                # Create and Add Buttons
                self.buttonsMetadata.append(QPushButton("Header"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, True))(index))
                self.panelLayout.addWidget(self.buttonsMetadata[-1], baseIndex + index, 3)
                
                self.buttonsMetadata.append(QPushButton("Plot"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, False))(index))
                self.panelLayout.addWidget(self.buttonsMetadata[-1], baseIndex + index, 4)

            elif (isinstance(meta, astropy.io.fits.hdu.table.TableHDU)):
                # Create and Add Labels
                self.labelsMetadata.append(QLabel(str(self.hdul[index].name)))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 0)

                self.labelsMetadata.append(QLabel("ASCII"))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 1)

                self.labelsMetadata.append(QLabel(f"({len(self.hdul[index].data[0])},{self.hdul[index].data.shape[0]})"))
                self.panelLayout.addWidget(self.labelsMetadata[-1], baseIndex + index, 2)

                # Create and Add Buttons
                self.buttonsMetadata.append(QPushButton("Header"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, True))(index))
                self.panelLayout.addWidget(self.buttonsMetadata[-1], baseIndex + index, 3)
                
                self.buttonsMetadata.append(QPushButton("Plot"))
                self.buttonsMetadata[-1].clicked.connect((lambda i: lambda: self.showMetadata(i, False))(index))
                self.panelLayout.addWidget(self.buttonsMetadata[-1], baseIndex + index, 4)
            else:
                print("Type not recognized")


        self.panelLayout.addWidget(self.loadCompareImageButton, 20, 1)

        self.panelLayout.addWidget(self.labelFileNameCompare, 21, 0)
        self.panelLayout.addWidget(self.filenameCompare, 21, 1)

        # Division for metadata

        self.panelLayout.addWidget(self.showDataButton, 40, 1)

        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.panelLayout.addItem(verticalSpacer)

        # Create layout for grid
        # -------------------------------------------------------------------- #
        self.main_layoutImageData.addLayout(self.panelLayout, 0, 0)
        self.setLayout(self.main_layoutImageData)
        # -------------------------------------------------------------------- #

        self.filename.setToolTip(_filename)

        # Create label for fileName
        if len(_filename) > 96:
            filename = "..." + _filename[-96:]
        else:
            filename = _filename

        self.filename.setText(filename)


    def showMetadata(self, indexMeta, isHeader):
        meta = ShowMeta(self, self.hdul[indexMeta], isHeader)
        meta.show()

        