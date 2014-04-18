# -*- coding: utf-8 -*-
"""
Created on 2014-04-18

@author: Hengkai Guo
"""

from PyQt4 import QtCore, QtGui
from Ui_SettingWindow import Ui_SettingWindow
from initParameter import initParameter
from dict4ini import DictIni
import DataBase as db
import os, sys

class SettingWindow(QtGui.QMainWindow, Ui_SettingWindow):
    def __init__(self):
        super(SettingWindow, self).__init__()
        self.setupUi(self)
        
        self.msgLabel = QtGui.QLabel()
        self.msgLabel.setMinimumSize(self.msgLabel.sizeHint())
        self.msgLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.msgLabel.setStyleSheet("QLabel{padding-left: 8px}")
        self.statusbar.addWidget(self.msgLabel)
        
        self.actionInit.triggered.connect(self.initParameter)
        self.actionMean.triggered.connect(self.saveMeanContour)
        
        self.ini = DictIni('segment.ini')
    
    def initParameter(self):
        nameList, repeat_time = initParameter(self.ini)
        self.showErrorMessage("Success initialization", "Files: " + str(nameList) + "\n" + "Repeat time: %d" % repeat_time)
    def saveMeanContour(self):
        seq = self.ini.parameter.sequence
        cnt = len(self.ini.file.names)
        # TO BE DONE
    def showMessageOnStatusBar(self, text):
        self.msgLabel.setText(text)
    def getMessageOnStatusBar(self):
        return str(self.msgLabel.text())
    def showErrorMessage(self, title, message):
        QtGui.QMessageBox.information(self, title, message)
    def show(self):
        super(SettingWindow, self).show()
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = SettingWindow()
    window.show()
    sys.exit(app.exec_())
