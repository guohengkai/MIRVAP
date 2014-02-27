# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

from MIRVAP.Core.GuiBase import GuiBase
from PyQt4 import QtGui
import sys
from MainWindow import MainWindow

class PyQtGui(GuiBase):
    def __init__(self):
        super(PyQtGui, self).__init__()
        self.app = QtGui.QApplication(sys.argv)
        self.win = MainWindow(self)
        
    def getFileNames(self, *args):
        return self.win.getFileNames(*args)
    def getDataIndexes(self):
        return self.win.getDataIndexes()
    def showErrorMessage(self, title, message):
        return self.win.showErrorMessage(title, message)
    def showMessageOnStatusBar(self, text):
        return self.win.showMessageOnStatusBar(text)
    def getMessageOnStatusBar(self):
        return self.win.getMessageOnStatusBar()
    def addNewDataView(self, data):
        return self.win.addNewDataView(data)
    def startApplication(self):        
        self.win.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    PyQtGui().startApplication()
