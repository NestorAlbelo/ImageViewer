from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QWidget
from PyQt5.uic import loadUi

class Alert(QDialog):
    def __init__(self, alertString):
        super(Alert, self).__init__()
        loadUi("GUIs/Alert.ui", self)
        self.alertLabel.setText(alertString)