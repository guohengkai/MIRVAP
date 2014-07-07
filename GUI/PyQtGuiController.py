# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

from MIRVAP.Core.GuiControllerBase import GuiControllerBase
from PyQt4 import QtGui
import sys
from MainWindow import MainWindow

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
        fixedIndex = self.getDataIndex(names, "Fixed image")
        if fixedIndex is not None:
            movingIndex = self.getDataIndex(names, "Moving image")
            if movingIndex is not None:
                return (fixedIndex, movingIndex)
    def getInputName(self, window):
        name, ok = QtGui.QInputDialog.getText(self.win, "Enter the name", 
                "Name:", QtGui.QLineEdit.Normal, window.getName())
        return name, ok
    def getInputPara(self, window, title, initial = 0.0):
        data, ok = QtGui.QInputDialog.getDouble(self.win, "Enter the " + title.lower(), 
                title.capitalize() + ":", initial)
        return data, ok
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
    PyQtGuiController().startApplication()
