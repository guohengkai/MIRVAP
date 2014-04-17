# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""

from PyQt4 import QtCore, QtGui
from Ui_MdiChild import Ui_MdiChild
import DataBase as db
from ResultImageView import ResultImageView

class MdiChildBase(QtGui.QMainWindow):
    def __init__(self, gui):
        super(MdiChildBase, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gui = gui
        self.isShow = False
    def setQVTKWidget(self):
        raise NotImplementedError('Method "setQVTKWidget" Not Impletemented!')
    def show(self):
        super(MdiChildBase, self).show()
        self.isShow = True
        # In order to get the correct size of window, it can't be put in the __init__ function
        self.setQVTKWidget()
    def getName(self):
        raise NotImplementedError('Method "getName" Not Impletemented!')
    def getData(self, key):
        raise NotImplementedError('Method "getData" Not Impletemented!')
    def closeEvent(self, event):
        self.isShow = False

class MdiChildLoad(MdiChildBase, Ui_MdiChild):
    def __init__(self, gui, index):
        super(MdiChildLoad, self).__init__(gui)
        self.setupUi(self)
        
        self.index = index
        self.setWindowTitle(self.getName())
        
        self.widgetView = ResultImageView(self)
        self.viewIndex = self.gui.win.resultIndex
        
        self.type = 'load'
    def getName(self):
        name = self.getData().getName()
        if not name:
            name = 'Data %d' % self.index
            self.getData().setName(name)
        return name
    def getData(self, key = None):
        return self.gui.dataModel[self.index]
    def setQVTKWidget(self):
        self.widgetView.setWidgetView(self.qvtkWidget)
    def setPlugin(self, plugin, index):
        self.widgetView.setPlugin(plugin, index)
    def setView(self, view, index):
        instance = view(self)
        if (instance.type != self.type and instance.type != 'any') or (self.getData().getDimension() not in instance.datatype):
            return False
        self.widgetView = instance
        self.viewIndex = index
        self.setQVTKWidget()
        return True
    def save(self):
        if self.isShow:
            self.widgetView.save()
    
    def closeEvent(self, event):
        super(MdiChildLoad, self).closeEvent(event)
        self.save()
        self.gui.showMessageOnStatusBar("")
        event.accept()

