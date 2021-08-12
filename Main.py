from LoadData import LoadData
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

    def getWorkingDirectory(self):
        return self.workingDirectory
    
    def setWorkingDirectory(self, newPath=""):
        if newPath:
            self.workingDirectory = '/'.join(newPath.split('/')[0:-1])

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open File", self.workingDirectory)[0]

        if (fileName):
            self.setWorkingDirectory(fileName)

            currentFile = LoadData(self, fileName)
            currentFile.move(50, 100)
            currentFile.show()
            self.openedFiles.append(currentFile) 

app = QApplication(sys.argv)
mainWindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.setFixedSize(200, 400)
widget.move(50, 50)
widget.show()
sys.exit(app.exec_())
