import sys, getopt
import os
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
import argparse
import math

# Load local libs
from LoadFits import LoadFits
from LoadBinary import LoadBinary

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QWidget
from PyQt5.uic import loadUi

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("GUIs/MainWindow.ui", self)
        self.openFileButton.clicked.connect(self.openFile)
        self.openedFiles = []
        self.workingDirectory = os.path.expanduser('~')

        # Remove this line
        self.openFile()

    def getWorkingDirectory(self):
        return self.workingDirectory
    
    def setWorkingDirectory(self, newPath=""):
        if newPath:
            self.workingDirectory = '/'.join(newPath.split('/')[0:-1])

    def openFile(self):
        #fileName = QFileDialog.getOpenFileName(self, "Open File", self.workingDirectory)[0]
        fileName = "0000029404.phi"
        fileName = "/home/albelo/Downloads/STP-136/solo_L0_phi-hrt-flat_0667134081_V202103221851C_0162201100.fits"
        self.setWorkingDirectory(fileName)

        if (fileName.endswith(".fits")):
            fitsFile = LoadFits(self, fileName)
            fitsFile.move(50, 100)
            fitsFile.show()
            self.openedFiles.append(fitsFile)
        else:
            binaryFile = LoadBinary(self, fileName)
            binaryFile.move(50, 100)
            binaryFile.show()

            self.openedFiles.append(binaryFile)   

app = QApplication(sys.argv)
mainWindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.setFixedSize(200, 400)
widget.show()
sys.exit(app.exec_())