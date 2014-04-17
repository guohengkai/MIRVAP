# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""

from GuiControllerBase import GuiControllerBase
from PyQt4 import QtGui
from MainWindow import MainWindow
import sys

class PyQtGuiController(GuiControllerBase):
    def __init__(self):
        super(PyQtGuiController, self).__init__()
        self.app = QtGui.QApplication(sys.argv)
        self.win = MainWindow(self)
    def getDirName(self, title, dir, filter):
        temp = QtGui.QFileDialog.getExistingDirectory(self.win, title, dir)
        return str(temp)
    def getFileNames(self, title, dir, filter):
        temp = QtGui.QFileDialog.getOpenFileNames(self.win, title, dir, filter)
        fileNames = map(str, temp)
        return fileNames
    def getSaveName(self, title, dir, filter):
        temp = QtGui.QFileDialog.getSaveFileName(self.win, title, dir, filter)
        fileName = str(temp)
        return fileName
    def getInputName(self, window):
        name, ok = QtGui.QInputDialog.getText(self.win, "Enter the name", 
                "Name:", QtGui.QLineEdit.Normal, window.getName())
        return name, ok
    def getInputPara(self, window, title, initial = 0.0):
        data, ok = QtGui.QInputDialog.getDouble(self.win, "Enter the " + title.lower(), 
                title.capitalize() + ":", initial)
        return data, ok
    def showMessageOnStatusBar(self, text):
        return self.win.showMessageOnStatusBar(text)
    def getMessageOnStatusBar(self):
        return self.win.getMessageOnStatusBar()
    def addNewDataView(self, data):
        return self.win.addNewDataView(data)
    def startApplication(self): 
        self.win.show()
        sys.exit(self.app.exec_())

