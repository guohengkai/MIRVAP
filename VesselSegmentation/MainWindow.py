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
        
        self.initParameter()
        
        self.loadData(self.ini.parameter.current)
        self.widgetView = ResultImageView(self)
    def getData(self, key = None):
        return self.data
    def initParameter(self):
        # ini: (1) file: names(list), savedir, datadir;
        #      (2) parameter: current, repeat, sequence(list)
        self.ini = DictIni('segment.ini')
        if not os.path.exists(self.ini.file.savedir):
            os.mkdir(self.ini.file.savedir)
        self.index = self.ini.parameter.current
    def loadData(self, index):
        dataname = self.ini.file.names[index]
        dir = self.ini.file.datadir + dataname
        data, info = db.loadMatData(dir)
        
        dataname = str(index) + '.mat'
        dir = self.ini.file.savedir + dataname
        point = db.loadMatPoint(dir)
        
        self.data = db.BasicData(data, info, point)
    def saveData(self, index):
        dataname = str(index) + '.mat'
        dir = self.ini.file.savedir + dataname
        db.saveMatPoint(dir, self.data)
        
    def saveAndNext(self):
        self.saveData(self.index)
        self.gui.showErrorMessage('Success', 'Save sucessfully!')
        self.index += 1
        if self.index < len(self.ini.file.names):
            self.loadData(self.index)
        else:
            self.gui.showErrorMessage('Congratulation', 'Your task has finished!')
    def viewData(self):
        pass
    def setQVTKWidget(self):
        self.widgetView.setWidgetView(self.qvtkWidget)
    def showMessageOnStatusBar(self, text):
        self.msgLabel.setText(text)
    def getMessageOnStatusBar(self):
        return str(self.msgLabel.text())
    def show(self):
        super(MainWindow, self).show()
        self.setQVTKWidget()
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure to quit?", 
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
