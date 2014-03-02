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
        # The argument need to be setted
        temp = QtGui.QFileDialog.getOpenFileNames()
        fileNames = map(str, temp)
        return fileNames
    def getReloadDataIndex(self):
        if self.dataModel.getCount() == 0:
            self.showErrorMessage('Error', 'There\'re no enough data!')
            return
        names = self.dataModel.getNameDict()
        return self.getDataIndex(names, "Select the data to be reloaded")
    def getDataIndex(self, names, word):
        items = names.keys()
        item, ok = QtGui.QInputDialog.getItem(self.win, word, "Data:", items, 0, False)
        if ok and item:
            item = str(item)
            index = int(names[item])
            del names[item]
            return index
    def getRegisterDataIndex(self):
        if self.dataModel.getCount() < 2:
            self.showErrorMessage('Error', 'There\'re no enough data!')
            return
        names = self.dataModel.getNameDict()
        fixedIndex = self.getDataIndex(names, "Select the fixed image")
        if fixedIndex is not None:
            movingIndex = self.getDataIndex(names, "Select the moving image")
            if movingIndex is not None:
                return (fixedIndex, movingIndex)
    def showErrorMessage(self, title, message):
        QtGui.QMessageBox.information(self.win, title, message)
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
