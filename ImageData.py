from types import FrameType
import PyQt5
import numpy as np
import matplotlib.pyplot as plt
import platform
from mpl_toolkits.mplot3d import Axes3D
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *#QApplication, QDialog, QFileDialog, QWidget, QVBoxLayout, 
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ImageScaling import *

import time

class ImageData(QDialog):
    def __init__(self, parent, _mainData, _compareData = None):
        super(ImageData, self).__init__(parent)

        self.mainData = _mainData
        self.compareData = _compareData
        self.indexCurrentImage = 0
        self.EVE_NAN = -2147483648

        self.refAxes = 0

        self.createUI()

    def replotFigure(self):

        self.fig.clear(True) 

        # There is not data to compare with
        if (self.compareData is None):

            if (self.showAll.isChecked()):
                self.indexImageLabel.setText(f"")
                self.prevImageButton.setEnabled(False)
                self.nextImageButton.setEnabled(False)

                xPlot = self.gridNumber()
                yPlot = int(self.mainData.frames / xPlot)

                currentData = np.copy(self.mainData.data)
                
                # Remove NaNs
                if (self.removeNaNs.isChecked()):
                    currentData[currentData == (self.EVE_NAN)] = 0

                self.showAllImages(currentData, xPlot, yPlot)

            else:
                self.prevImageButton.setEnabled(True)
                self.nextImageButton.setEnabled(True)

                currentData = np.copy(self.mainData.data[self.indexCurrentImage])
                
                # Remove NaNs
                if (self.removeNaNs.isChecked()):
                    currentData[currentData == (self.EVE_NAN)] = 0

                self.showOneImage(currentData)

        else:

            # If a type convertion is required
            if (self.convertDataTypes.isChecked()):
                currentData, currentDataCompare = self.convertData()
            else:
                currentData = np.copy(self.mainData.data[self.indexCurrentImage])    
                currentDataCompare = np.copy(self.compareData.data[self.indexCurrentImage]) 

            # Remove NaNs
            if (self.removeNaNs.isChecked()):
                currentData[currentData == (self.EVE_NAN)] = 0   
                currentDataCompare[currentDataCompare == (self.EVE_NAN)] = 0   

            self.compareImages(currentData, currentDataCompare)
            
        # Flip vertically to match FV representation
        if (self.flipVertically.isChecked()):
            self.fig.gca().invert_yaxis()
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def showOneImage(self, data):

        # Variables for more readability
        X = self.mainData.width
        Y = self.mainData.height

        # Activate labels
        self.toggleMetrics(True)

        # Set message for current index
        self.indexImageLabel.setText(f"Image {self.indexCurrentImage + 1} of {self.mainData.frames}")

        data, vmin, vmax = self.scalingFunctions(data)        

        # Create squared ROI for mean calculation of 256 pixels
        ROICenter = data[int(X/2) - 128:int(X/2) + 128,int(Y/2) - 128:int(Y/2) + 128]

        # Set Max, Min and Mean
        indexMin = np.argmin(data)
        posXMin = int(indexMin/X)
        posYMin = int(indexMin - int(indexMin/X) * X)
        minValue = data.min()
        indexMax = np.argmax(data)
        posXMax = int(indexMax/X)
        posYMax = int(indexMax - int(indexMax/X) * X)
        maxValue = data.max()

        self.minValue.setText(f"{minValue} ({posXMin}, {posYMin})")
        self.maxValue.setText(f"{maxValue} ({posXMax}, {posYMax})")
        self.meanCenter.setText(f"{np.mean(ROICenter)}")

        self.refAxes = self.fig.add_subplot(1, 1, 1)
        self.refAxes.title.set_text(f"Image {self.indexCurrentImage + 1}")
        self.refAxes.imshow(data, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vmin, vmax=vmax)            

    def showAllImages(self, data, xPlot, yPlot):
        # Set labels to empty
        self.minValue.setText("")
        self.maxValue.setText("")
        self.meanCenter.setText("")

        # Disable labels
        self.toggleMetrics(False)

        for x in range(xPlot):
            for y in range(yPlot):
                data[x * yPlot + y], vmin, vmax = self.scalingFunctions(data[x * yPlot + y])

                if (x == 0 and y == 0):
                    self.refAxes = self.fig.add_subplot(xPlot, yPlot, (x * yPlot + y) + 1)
                    self.refAxes.title.set_text("Image 0")
                    self.refAxes.imshow(data[x * yPlot + y], cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vmin, vmax=vmax)
                else:
                    self.ax = self.fig.add_subplot(xPlot, yPlot, (x * yPlot + y) + 1, sharex=self.refAxes, sharey=self.refAxes)
                    self.ax.title.set_text("Image " + str(x * yPlot + y))
                    self.ax.imshow(data[x * yPlot + y], cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vmin, vmax=vmax)
        
    def compareImages(self, dataInput, dataCompare):

        # Set message for current index
        self.indexImageLabel.setText(f"Image {self.indexCurrentImage + 1} of {self.mainData.frames}")

        dataInput, vminInput, vmaxInput = self.scalingFunctions(dataInput)        
        dataCompare, vminCompare, vmaxCompare = self.scalingFunctions(dataCompare)        

        numFigures = 2

        if (self.showDifference.isChecked()):
            numFigures = 3

            # Enable UIs
            self.invertDiffLabel.setEnabled(True)
            self.invertDiff.setEnabled(True)
            self.toggleMetrics(True)
        
            # Variables for more readability
            X = self.mainData.width
            Y = self.mainData.height

            if (self.invertDiff.isChecked()):
                differenceImage = dataCompare - dataInput
            else:
                differenceImage = dataInput - dataCompare

            differenceImage, vminDiff, vmaxDiff = self.scalingFunctions(differenceImage)        

            # Create ROI for mean calculation
            ROICenter = differenceImage[int(X/2) - 128:int(X/2) + 128,int(Y/2) - 128:int(Y/2) + 128]

            # Set Max, Min and Mean
            indexMax = np.argmax(differenceImage)
            indexMin = np.argmin(differenceImage)
            posXMin = int(indexMin/X)
            posYMin = int(indexMin - int(indexMin/X) * X)
            minValue = differenceImage.min()
            posXMax = int(indexMax/X)
            posYMax = int(indexMax - int(indexMax/X) * X)
            maxValue = differenceImage.max()

            self.minValue.setText(f"{minValue} ({posXMin}, {posYMin})")
            self.maxValue.setText(f"{maxValue} ({posXMax}, {posYMax})")
            self.meanCenter.setText(str(np.mean(ROICenter)))

        else:
            self.minValue.setText("")
            self.maxValue.setText("")
            self.meanCenter.setText("")

            self.invertDiffLabel.setEnabled(False)
            self.invertDiff.setEnabled(False)
            self.toggleMetrics(False)

        # Plot images            
        self.refAxes = self.fig.add_subplot(1, numFigures, 1)
        self.refAxes.title.set_text(self.mainData.filePath.split('/')[-1])
        self.refAxes.imshow(dataInput, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vminInput, vmax=vmaxInput)
        self.ax = self.fig.add_subplot(1, numFigures, 2, sharex=self.refAxes, sharey=self.refAxes)
        self.ax.title.set_text(self.compareData.filePath.split('/')[-1])
        self.ax.imshow(dataCompare, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vminCompare, vmax=vmaxCompare)

        if (self.showDifference.isChecked()):
            self.ax = self.fig.add_subplot(1, numFigures, 3, sharex=self.refAxes, sharey=self.refAxes)
            self.ax.title.set_text("Difference")
            self.ax.imshow(differenceImage, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vminDiff, vmax=vmaxDiff)
    
    def increaseIndex(self):
        self.indexCurrentImage = (self.indexCurrentImage + 1) % self.mainData.frames
        self.replotFigure()
    
    def decreaseIndex(self):
        self.indexCurrentImage = (self.indexCurrentImage - 1) % self.mainData.frames
        self.replotFigure()

    def toggleMetrics(self, state):
        self.minValue.setEnabled(state)
        self.minValueLabel.setEnabled(state)
        self.maxValue.setEnabled(state)
        self.maxValueLabel.setEnabled(state)
        self.meanCenter.setEnabled(state)
        self.meanCenterLabel.setEnabled(state)

    def gridNumber(self):
        for x in range(self.mainData.frames + 1, 0, -1):
            if(self.mainData.frames % x == 0 and x <= 5):
                if (self.mainData.frames / x < x):
                    return int(self.mainData.frames / x)
                else:
                    return (x)

    def scalingFunctions(self, data):

        # Algorithm Scaling Image
        if(self.scaleAlgorithm.currentText() == "Log"):
            data[data <= 0] = 1
            data = np.log(data)
        elif (self.scaleAlgorithm.currentText() == "Power"):
            data = np.power(data, 2)
        elif (self.scaleAlgorithm.currentText() == "Square Root"):
            data[data <= 0] = 1
            data = np.sqrt(data)
        elif (self.scaleAlgorithm.currentText() == "Sin"):
            data = np.sin(data / np.abs(data).max())
        elif (self.scaleAlgorithm.currentText() == "ArcSin"):
            data = np.arcsin(data / (np.abs(data).max())) 
        elif (self.scaleAlgorithm.currentText() == "Histogram"):
            data = image_histogram_equalization(data, 1024)

        # Scale Range
        if (self.scaleRange.currentText() == "Min-Max"):
            minValue = data.min()
            maxValue = data.max()
        elif (self.scaleRange.currentText() == "ZScale"):
            minValue, maxValue = zscale(data)

        return data, minValue, maxValue

    def convertData(self):
        currentMainData = np.copy(self.mainData.data[self.indexCurrentImage])    
        currentCompareData = np.copy(self.compareData.data[self.indexCurrentImage])

        # Convert both images to float if their datatypes are differents
        if (self.mainData.dataType != self.compareData.dataType):
            currentMainData = currentMainData.astype(np.float)
            currentCompareData = currentCompareData.astype(np.float)

        # Check if bytes per pixel matches
        if (self.mainData.bytesPerPixel < self.compareData.bytesPerPixel):
            # 8 bits per byte
            scaling = 1 << ((self.compareData.bytesPerPixel - self.mainData.bytesPerPixel) * 8)
            currentMainData = currentMainData.astype(type(currentCompareData[0][0])) * scaling
        
        if (self.compareData.bytesPerPixel < self.mainData.bytesPerPixel):
            # 8 bits per byte
            scaling = 1 << ((self.mainData.bytesPerPixel - self.compareData.bytesPerPixel) * 8)
            currentCompareData = currentCompareData.astype(type(currentMainData[0][0])) * scaling

        return currentMainData, currentCompareData

    def createUI(self):
        
        if (self.compareData == None):
            self.setWindowTitle(f"{self.mainData.filePath.split('/')[-1]}")
        else:
            self.setWindowTitle(f"{self.mainData.filePath.split('/')[-1]} vs {self.compareData.filePath.split('/')[-1]}")

        # Create figure for this dataset
        self.fig, self.refAxes = plt.subplots(1, 1)

        # this is the Canvas Widget that 
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.fig)
   
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Labels
        # -------------------------------------------------------------------- #
        self.cmapLabel = QLabel("CMap:")
        self.scaleRangeLabel = QLabel("Scale Range:")
        self.scaleAlgorithmLabel = QLabel("Scale Algorithm:")
        self.removeNaNsLabel = QLabel("Remove NaNs:")
        self.showAllLabel = QLabel("Show All:")
        self.minValueLabel = QLabel("Min Value:")
        self.minValue = QLabel("0")
        self.maxValueLabel = QLabel("Max Value:")
        self.maxValue = QLabel("0")
        self.meanCenterLabel = QLabel("Mean Center:")
        self.meanCenter = QLabel("0")
        self.showDifferenceLabel = QLabel("Show Difference:")
        self.invertDiffLabel = QLabel("Invert Difference:")
        self.flipVerticallyLabel = QLabel("Flip Vertically:")
        self.convertDataTypesLabel = QLabel("Convert datatypes:")
        self.indexImageLabel = QLabel("")
        # -------------------------------------------------------------------- #

        # ComboBoxes
        # -------------------------------------------------------------------- #
        self.cmap = QComboBox()
        self.scaleRange = QComboBox()
        self.scaleAlgorithm = QComboBox()

        self.cmap.addItems(["gray","Spectral","YlOrBr","hsv","hot","Set1","gist_earth","nipy_spectral","tab10"])
        self.scaleRange.addItems(["Min-Max","ZScale"])
        self.scaleAlgorithm.addItems(["Linear", "Log", "Power", "Square Root", "Sin", "ArcSin", "Histogram"])
        # -------------------------------------------------------------------- #

        # CheckBoxes
        # -------------------------------------------------------------------- #
        self.removeNaNs = QCheckBox()
        self.showAll = QCheckBox()
        self.showDifference = QCheckBox()
        self.invertDiff = QCheckBox()
        self.flipVertically = QCheckBox()
        self.convertDataTypes = QCheckBox()
        # -------------------------------------------------------------------- #

        # Properties
        # -------------------------------------------------------------------- #
        # Bold
        boldFont=PyQt5.QtGui.QFont()
        boldFont.setBold(True)
        self.cmapLabel.setFont(boldFont)
        self.scaleRangeLabel.setFont(boldFont)
        self.scaleAlgorithmLabel.setFont(boldFont)
        self.removeNaNsLabel.setFont(boldFont)
        self.showAllLabel.setFont(boldFont)
        self.minValueLabel.setFont(boldFont)
        self.maxValueLabel.setFont(boldFont)
        self.meanCenterLabel.setFont(boldFont)
        self.showDifferenceLabel.setFont(boldFont)
        self.invertDiffLabel.setFont(boldFont)
        self.flipVerticallyLabel.setFont(boldFont)
        self.convertDataTypesLabel.setFont(boldFont)

        if (self.mainData.frames == 1):
            self.showAllLabel.setEnabled(False)
            self.showAll.setEnabled(False)
        # -------------------------------------------------------------------- #

        # Buttons
        # -------------------------------------------------------------------- #
        self.prevImageButton = QPushButton("Previous Image")
        self.nextImageButton = QPushButton("Next Image")
        # -------------------------------------------------------------------- #

        # Connect events
        # -------------------------------------------------------------------- #
        self.cmap.activated[str].connect(self.replotFigure)    
        self.scaleAlgorithm.activated[str].connect(self.replotFigure)    
        self.scaleRange.activated[str].connect(self.replotFigure)  

        self.removeNaNs.toggled.connect(self.replotFigure)
        self.showAll.toggled.connect(self.replotFigure)
        self.invertDiff.toggled.connect(self.replotFigure)
        self.showDifference.toggled.connect(self.replotFigure)
        self.flipVertically.toggled.connect(self.replotFigure)
        self.convertDataTypes.toggled.connect(self.replotFigure)

        self.prevImageButton.clicked.connect(self.decreaseIndex)
        self.nextImageButton.clicked.connect(self.increaseIndex) 
        # -------------------------------------------------------------------- #

        # Canvas
        # -------------------------------------------------------------------- #
        self.main_layoutImageData = QGridLayout()
        self.panelLayout = QGridLayout()
        self.canvasLayout = QVBoxLayout()
        # -------------------------------------------------------------------- #
        
        # Add Widgets
        # -------------------------------------------------------------------- #
        # Panel
        self.panelLayout.addWidget(self.cmapLabel, 0, 0)
        self.panelLayout.addWidget(self.cmap, 0, 1)

        self.panelLayout.addWidget(self.scaleRangeLabel, 1, 0)
        self.panelLayout.addWidget(self.scaleRange, 1, 1)

        self.panelLayout.addWidget(self.scaleAlgorithmLabel, 2, 0)
        self.panelLayout.addWidget(self.scaleAlgorithm, 2, 1)

        # Do not remove NaNs from floats.
        if ((not self.mainData.dataType.endswith("float")) and
            ((not self.compareData is None) and 
            (not self.compareData.dataType.endswith("float")))):
            self.panelLayout.addWidget(self.removeNaNsLabel, 3, 0)
            self.panelLayout.addWidget(self.removeNaNs, 3, 1)

        # If data to compare not exists
        if (self.compareData is None):
            self.panelLayout.addWidget(self.showAllLabel, 4, 0)
            self.panelLayout.addWidget(self.showAll, 4, 1)
        
        else:
            self.panelLayout.addWidget(self.showDifferenceLabel, 4, 0)
            self.panelLayout.addWidget(self.showDifference, 4, 1)

            self.panelLayout.addWidget(self.invertDiffLabel, 5, 0)
            self.panelLayout.addWidget(self.invertDiff, 5, 1)

            self.minValueLabel.setText("Min Value Diff:")
            self.maxValueLabel.setText("Max Value Diff:")
            self.meanCenterLabel.setText("Mean Center Diff:")

        self.panelLayout.addWidget(self.minValueLabel, 6, 0)
        self.panelLayout.addWidget(self.minValue, 6, 1)

        self.panelLayout.addWidget(self.maxValueLabel, 7, 0)
        self.panelLayout.addWidget(self.maxValue, 7, 1)
        
        self.panelLayout.addWidget(self.meanCenterLabel, 8, 0)
        self.panelLayout.addWidget(self.meanCenter, 8, 1)

        self.panelLayout.addWidget(self.flipVerticallyLabel, 9, 0)
        self.panelLayout.addWidget(self.flipVertically, 9, 1)

        # If we have data to compare with
        if (not self.compareData is None):
            # Check that the datatypes matches, otherwise insert UI to fix it
            if ((self.mainData.dataType != self.compareData.dataType) or
                (self.mainData.bytesPerPixel != self.compareData.bytesPerPixel)):
                self.panelLayout.addWidget(self.convertDataTypesLabel, 10, 0)
                self.panelLayout.addWidget(self.convertDataTypes, 10, 1)

        self.panelLayout.addWidget(self.indexImageLabel, 15, 0)

        self.panelLayout.addWidget(self.prevImageButton, 16, 0)
        self.panelLayout.addWidget(self.nextImageButton, 16, 1)

        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.panelLayout.addItem(verticalSpacer)

        # Canvas
        self.canvasLayout.addWidget(self.canvas)
        self.canvasLayout.addWidget(self.toolbar)
        # -------------------------------------------------------------------- #
            
        # Create layout for grid
        # -------------------------------------------------------------------- #
        self.main_layoutImageData.addLayout(self.panelLayout, 0, 0)
        self.main_layoutImageData.addLayout(self.canvasLayout, 0, 1, 1, 1)
        self.setLayout(self.main_layoutImageData)
        # -------------------------------------------------------------------- #

        # Exclude number of frames primes greater than 5 to use ShowAll
        if (self.mainData.frames in [7, 11, 13, 17, 19, 23]):
            self.showAllLabel.setEnabled(False)
            self.showAll.setEnabled(False)
            self.showAllLabel.setToolTip("The number of frames introduced are not compatible with this option.")

        self.showMaximized()

        self.replotFigure()