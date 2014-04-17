# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""


from PyQt4 import QtCore, QtGui
from Ui_SegmentationMainWindow import Ui_SegmentationMainWindow
from ResultImageView import ResultImageView
import DataBase as db
from dict4ini import DictIni
import os

class MainWindow(QtGui.QMainWindow, Ui_SegmentationMainWindow):
    def __init__(self, gui):
        super(MainWindow, self).__init__()
        self.gui = gui
        self.setupUi(self)
        
        self.msgLabel = QtGui.QLabel()
        self.msgLabel.setMinimumSize(self.msgLabel.sizeHint())
        self.msgLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.msgLabel.setStyleSheet("QLabel{padding-left: 8px}")
        self.statusbar.addWidget(self.msgLabel)
        
        self.actionNext.triggered.connect(self.saveAndNext)
        self.actionView.triggered.connect(self.viewData)
        
        self.error = self.initParameter()
        if self.error: # There's no valid ini file
            self.actionNext.setDisabled(True)
            self.actionView.setDisabled(True)
        
        self.loadData(self.ini.parameter.current)
        self.widgetView = ResultImageView(self)
    def getData(self, key = None):
        return self.data
    def initParameter(self):
        # ini: (1) file: names(list), savedir, datadir;
        #      (2) parameter: current, repeat, sequence(list)
        try:
            self.ini = DictIni('segment.ini')
            if not os.path.exists(self.ini.file.savedir):
                os.mkdir(self.ini.file.savedir)
            return False
        except Exception:
            return True
    def loadData(self, index):
        if self.error:
            self.data = None
            return
            
        dataname = self.ini.file.names[self.ini.parameter.sequence[index]]
        dir = self.ini.file.datadir + dataname
        data, info = db.loadMatData(dir)
        
        dataname = str(index) + '.mat'
        dir = self.ini.file.savedir + dataname
        point = db.loadMatPoint(dir)
        
        self.data = db.BasicData(data, info, point)
    def saveData(self, index):
        self.widgetView.save()
        dataname = str(index) + '.mat'
        dir = self.ini.file.savedir + dataname
        db.saveMatPoint(dir, self.data)
        
    def saveAndNext(self):
        self.saveData(self.ini.parameter.current)
        self.showErrorMessage('Success', 'Save sucessfully!')
        self.ini.parameter.current += 1
        if self.ini.parameter.current < len(self.ini.parameter.sequence):
            self.loadData(self.ini.parameter.current)
            self.setQVTKWidget()
        else:
            self.showErrorMessage('Congratulation', 'Your task has finished!')
            self.ini.parameter.current -= 1
    def viewData(self):
        self.saveData(self.ini.parameter.current)
        items = map(str, range(len(self.ini.parameter.sequence)))
        item, ok = QtGui.QInputDialog.getItem(self, "Select the data", "Index:", items, self.ini.parameter.current, False)
        if ok and item:
            item = int(item)
            if self.ini.parameter.current != item:
                self.ini.parameter.current = item
                self.loadData(self.ini.parameter.current)
                self.setQVTKWidget()
    def setQVTKWidget(self):
        self.widgetView.setWidgetView(self.qvtkWidget)
    def showMessageOnStatusBar(self, text):
        self.msgLabel.setText(text)
    def getMessageOnStatusBar(self):
        return str(self.msgLabel.text())
    def showErrorMessage(self, title, message):
        QtGui.QMessageBox.information(self, title, message)
    def show(self):
        super(MainWindow, self).show()
        self.setQVTKWidget()
        if self.error:
            self.showErrorMessage("File error", "Can't find a valid ini file!")
    def closeEvent(self, event):
        self.ini.save()
        if not self.error:
            self.saveData(self.ini.parameter.current)
        event.accept()
