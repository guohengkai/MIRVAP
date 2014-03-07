# -*- coding: utf-8 -*-
"""
Created on 2014-02-06

@author: Hengkai Guo
"""

from PyQt4 import QtCore, QtGui
from Ui_MdiChild import Ui_MdiChild
import MIRVAP.Core.DataBase as db
from WidgetView.ResultImageView import ResultImageView


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
    '''
        Move left button:     Modify window level
        Move middle button:   Pan the camera
        Wheel middle button:  Zoom the camera
        Move right button:    Slice through the image
        
        Press R Key:          Reset the Window/Level
        Press X Key:          Reset to a sagittal view
        Press Y Key:          Reset to a coronal view
        Press Z Key:          Reset to an axial view
        Press Left/Right Key: Slice through the image
    '''
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

class MdiChildRegistration(MdiChildLoad):
    def __init__(self, gui, index):
        super(MdiChildRegistration, self).__init__(gui, index)
        
        self.fixedIndex = self.getData().getFixedIndex()
        self.movingIndex = self.getData().getMovingIndex()
        
        self.setWindowTitle(self.getName())
        self.type = 'registration'
    def getData(self, key = 'result'):
        if key == 'result':
            return self.gui.dataModel[self.index]
        elif key == 'fix':
            return self.gui.dataModel[self.fixedIndex]
        elif key == 'move':
            return self.gui.dataModel[self.movingIndex]
    def getName(self):
        name = self.getData().getName()
        if not name:
            name = 'Result %d' % self.index
            self.getData().setName(name)
        return name

