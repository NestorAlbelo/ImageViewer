import numpy as np
import matplotlib.pyplot as plt
import platform
from mpl_toolkits.mplot3d import Axes3D
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QWidget
from PyQt5.uic import loadUi
from ImageScaling import *

import time

class ImageData(QDialog):
    def __init__(self, parent, _data, _dataName, _width, _height, _frames, 
                    _dataType, _isComplex, _isLittleEndian, _fileName, 
                    _dataCompare=None, _dataCompareName=None):
        super(ImageData, self).__init__(parent)
        loadUi("GUIs/ImageData.ui", self)

        self.dataInput = _data
        self.dataName = _dataName
        self.width = _width
        self.height = _height
        self.frames = _frames
        self.datatype = _dataType
        self.isComplex = _isComplex
        self.isLittleEndian = _isLittleEndian
        self.indexCurrentImage = 0
        self.dataCompare = _dataCompare
        self.dataCompareName = _dataCompareName

        self.dataInputCopy = None
        self.dataCompareCopy = None

        # Create figure for this dataset
        self.fig, self.ax = plt.subplots(1, 1)

        self.createWindow()
        self.replotFigure()

        # Connect events
        self.cmap.activated[str].connect(self.replotFigure)    
        self.scaleAlgorithm.activated[str].connect(self.replotFigure)    
        self.scaleRange.activated[str].connect(self.replotFigure)  

        self.removeNaNs.toggled.connect(self.replotFigure)
        self.showAll.toggled.connect(self.replotFigure)
        self.show3D.toggled.connect(self.replotFigure)
        self.invertDiff.toggled.connect(self.replotFigure)
        self.showDifference.toggled.connect(self.replotFigure)

        self.prevImageButton.clicked.connect(self.decreaseIndex)
        self.nextImageButton.clicked.connect(self.increaseIndex) 

        # Do not remove NaNs from floats.
        if (self.datatype.endswith("f4")):
            self.removeNaNs.setEnabled(False)

        # If the compare data exists, then disable
        if (not (self.dataCompare is None)):
            self.showAll.setEnabled(False)
            self.showAllLabel.setEnabled(False)
            self.show3D.setEnabled(False)
            self.show3DLabel.setEnabled(False)
            self.invertDiff.setEnabled(True)
            self.invertDiffLabel.setEnabled(True)
            self.showDifference.setEnabled(True)
            self.showDifferenceLabel.setEnabled(True)
            self.minValueLabel.setText("Min Value Diff:")
            self.maxValueLabel.setText("Max Value Diff:")
            self.meanCenterLabel.setText("Mean Center Diff:")

    def createWindow(self):    
        #fig.canvas.set_window_title(windowName)

        if (platform.system() == "Linux"):
            figManager = plt.get_current_fig_manager()
            figManager.window.showMaximized()
        plt.show()

    def replotFigure(self):

        # There is not data to compare with
        if ((self.dataCompare is None)):
            if (self.showAll.isChecked()):
                self.show3D.setEnabled(False)
                self.show3DLabel.setEnabled(False)
            else:
                self.show3D.setEnabled(True)
                self.show3DLabel.setEnabled(True)
            
            if (self.show3D.isChecked()):
                self.showAll.setEnabled(False)
                self.showAllLabel.setEnabled(False)
            else:
                self.showAll.setEnabled(True)
                self.showAllLabel.setEnabled(True)

        # Local Variables for more readability
        X = self.width
        Y = self.height

        self.fig.clear(True) 

        if (self.dataCompare is None):

            if(self.showAll.isChecked()):
                self.prevImageButton.setEnabled(False)
                self.nextImageButton.setEnabled(False)

                xPlot = 4
                yPlot = 6

                if (self.frames == 25):
                    xPlot = 5
                    yPlot = 5
                if (self.frames == 5):
                    xPlot = 1
                    yPlot = 5

                currentData = np.copy(self.dataInput)
                
                # Remove NaNs
                if (self.removeNaNs.isChecked()):
                    currentData[currentData == (-2147483647-1)] = 0

                self.showAllImages(currentData, xPlot, yPlot)

            else:
                self.prevImageButton.setEnabled(True)
                self.nextImageButton.setEnabled(True)

                currentData = np.copy(self.dataInput[self.indexCurrentImage])
                
                # Remove NaNs
                if (self.removeNaNs.isChecked()):
                    currentData[currentData == (-2147483647-1)] = 0

                self.showOneImage(currentData, X, Y)

        else:
            currentData = np.copy(self.dataInput[self.indexCurrentImage])    
            currentDataCompare = np.copy(self.dataCompare[self.indexCurrentImage]) 

            # Remove NaNs
            if (self.removeNaNs.isChecked()):
                currentData[currentData == (-2147483647-1)] = 0   
                currentDataCompare[currentDataCompare == (-2147483647-1)] = 0   

            self.compareImages(currentData, currentDataCompare, X, Y)
            # currentData = np.copy(self.dataInput[self.indexCurrentImage])
            # ROICenter = currentData[int(X/2) - 100:int(X/2) + 100,int(Y/2) - 100:int(Y/2) + 100]

            # # Set Max, Min and Mean
            # indexMax = np.argmax(currentData)
            # indexMin = np.argmin(currentData)
            # posXMin = int(indexMin/X)
            # posYMin = int(indexMin - int(indexMin/X) * X)
            # minValue = currentData.min()
            # posXMax = int(indexMax/X)
            # posYMax = int(indexMax - int(indexMax/X) * X)
            # maxValue = currentData.max()

            # self.minValue.setText(f"{minValue} ({posXMin}, {posYMin})")
            # self.maxValue.setText(f"{maxValue} ({posXMax}, {posYMax})")
            # self.meanCenter.setText(str(np.mean(ROICenter)))

            # # Plot image
            # self.ax.imshow(currentData, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=minValue, vmax=maxValue)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def showOneImage(self, data, X, Y):
        # Activate labels
        self.toggleMetrics(True)

        # Set message for current index
        self.indexImageLabel.setText(f"Image {self.indexCurrentImage + 1} of {self.frames}")

        data, vmin, vmax = self.scalingFunctions(data)        

        # Create ROI for mean calculation
        ROICenter = data[int(X/2) - 100:int(X/2) + 100,int(Y/2) - 100:int(Y/2) + 100]

        # Set Max, Min and Mean
        indexMax = np.argmax(data)
        indexMin = np.argmin(data)
        posXMin = int(indexMin/X)
        posYMin = int(indexMin - int(indexMin/X) * X)
        minValue = data.min()
        posXMax = int(indexMax/X)
        posYMax = int(indexMax - int(indexMax/X) * X)
        maxValue = data.max()

        self.minValue.setText(f"{minValue} ({posXMin}, {posYMin})")
        self.maxValue.setText(f"{maxValue} ({posXMax}, {posYMax})")
        self.meanCenter.setText(str(np.mean(ROICenter)))

        # Plot image in 2D
        if (not self.show3D.isChecked()):
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.title.set_text(self.dataName)
            self.ax.imshow(data, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vmin, vmax=vmax)

        # Plot image in 3D
        else:
            # create the x and y coordinate arrays (here we just use pixel indices)
            xx, yy = np.mgrid[0:data.shape[0], 0:data.shape[1]]

            print(f"XX: {xx}")
            print(f"YY: {yy}")

            # create the figure
            # self.ax = self.fig.gca(projection='3d')
            # self.ax.plot_surface(xx, yy, data ,rstride=1, cstride=1, cmap=plt.cm.get_cmap(self.cmap.currentText()), linewidth=0)
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.imshow(data, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vmin, vmax=vmax)
            

        
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

                self.ax = self.fig.add_subplot(xPlot, yPlot, (x * yPlot + y) + 1)
                self.ax.imshow(data[x * yPlot + y], cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vmin, vmax=vmax)
        
    def compareImages(self, dataInput, dataCompare, X, Y):
        # Set message for current index
        self.indexImageLabel.setText(f"Image {self.indexCurrentImage + 1} of {self.frames}")

        if (self.invertDiff.isChecked()):
            differenceImage = dataCompare - dataInput
        else:
            differenceImage = dataInput - dataCompare

        dataInput, vminInput, vmaxInput = self.scalingFunctions(dataInput)        
        dataCompare, vminCompare, vmaxCompare = self.scalingFunctions(dataCompare)        
        differenceImage, vminDiff, vmaxDiff = self.scalingFunctions(differenceImage)        

        # Create ROI for mean calculation
        ROICenter = differenceImage[int(X/2) - 100:int(X/2) + 100,int(Y/2) - 100:int(Y/2) + 100]

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

        # Plot images
        numFigures = 2

        if (self.showDifference.isChecked()):
            numFigures = 3
            self.ax = self.fig.add_subplot(1, numFigures, 3)
            self.ax.title.set_text("Difference")
            self.ax.imshow(differenceImage, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vminDiff, vmax=vmaxDiff)
            
        self.ax = self.fig.add_subplot(1, numFigures, 1)
        self.ax.title.set_text(self.dataName)
        self.ax.imshow(dataInput, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vminInput, vmax=vmaxInput)
        self.ax = self.fig.add_subplot(1, numFigures, 2)
        self.ax.title.set_text(self.dataCompareName)
        self.ax.imshow(dataCompare, cmap=plt.cm.get_cmap(self.cmap.currentText()), vmin=vminCompare, vmax=vmaxCompare)
    

    def increaseIndex(self):
        self.indexCurrentImage = (self.indexCurrentImage + 1) % self.frames
        self.replotFigure()
    
    def decreaseIndex(self):
        self.indexCurrentImage = (self.indexCurrentImage - 1) % self.frames
        self.replotFigure()

    def toggleMetrics(self, state):
        self.minValue.setEnabled(state)
        self.minValueLabel.setEnabled(state)
        self.maxValue.setEnabled(state)
        self.maxValueLabel.setEnabled(state)
        self.meanCenter.setEnabled(state)
        self.meanCenterLabel.setEnabled(state)

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

        