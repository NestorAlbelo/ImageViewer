from PyQt5 import QtWidgets, QtGui
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
import numpy as np
import sys

class ShowMeta(QDialog):
    def __init__(self, parent, _metadata, _isHeader, title="Metadata"):
        super(ShowMeta, self).__init__(parent)
        
        self.metadata = _metadata
        self.isHeader = _isHeader

        self.setWindowTitle(title)
        self.createUI()

    def createUI(self):
        self.widget = QLabel("ERROR Loading Metadata")

        if (self.isHeader):
            self.widget = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
            
            self.label = QLabel(self.metadata.header.tostring('\n'))
            self.widget.setWidget(self.label)

            self.resize(QSize(800, 1000))

        else:
            numCols = 0
            data = {}

            try:
                numCols = int(self.metadata.header["TFIELDS"])

                # Create dict of data
                for i in range(numCols):
                    data[self.metadata.header[f"TTYPE{i+1}"]] = [item[i] for item in self.metadata.data]
            except:
                numCols = 1
                data["Data"] = self.metadata.data
        
            self.widget = QTableWidget()
            self.widget.setColumnCount(len(data))
            self.widget.setRowCount(len(data[list(data.keys())[0]]))

            colHeaders = []
            for n, key in enumerate(data.keys()):
                colHeaders.append(f" {key} ")
                for m, item in enumerate(data[key]):
                    self.widget.setItem(m, n, QTableWidgetItem(str(f"{item}  ")))
            self.widget.setHorizontalHeaderLabels(colHeaders)
            self.widget.move(0,0)

            stylesheetHeader = "::section{font: bold}"

            self.widget.setAlternatingRowColors(True)
            self.widget.setStyleSheet("alternate-background-color: Lightgrey;background-color: white;")
            self.widget.horizontalHeader().setStyleSheet(stylesheetHeader)
            self.widget.resizeColumnsToContents()
            self.widget.resizeRowsToContents()

            tableWidth = sum([self.widget.columnWidth(i) for i in range(len(colHeaders))]) + 120

            # Set a max
            if (tableWidth > 1700):
                tableWidth = 1700

            self.resize(QSize(tableWidth, 700))


        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QGridLayout()
        self.layout.addWidget(self.widget, 0, 0) 
        self.setLayout(self.layout) 