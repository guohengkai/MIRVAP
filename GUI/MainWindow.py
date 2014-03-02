# -*- coding: utf-8 -*-
"""
Created on 2014-02-01

@author: Hengkai Guo
"""


from PyQt4 import QtCore, QtGui
from Ui_MainWindow import Ui_MainWindow
from MdiChild import MdiChildLoad, MdiChildRegistration
import MIRVAP.Core.DataBase as db
import MIRVAP.Core.ScriptBase as sb
import MIRVAP.Core.GuiBase as gb
from functools import partial

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, gui):
        super(MainWindow, self).__init__()
        self.gui = gui
        self.setupUi(self)
        
        self.msgLabel = QtGui.QLabel()
        self.msgLabel.setMinimumSize(self.msgLabel.sizeHint())
        self.msgLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.msgLabel.setStyleSheet("QLabel{padding-left: 8px}")
        self.statusbar.addWidget(self.msgLabel)
        
        self.menuScript = {'Load': self.menuLoad, 'Registration': self.menuRegister, 
            'Analysis': self.menuAnalysis}
        self.script = {}
        self.actionScript = {}
        self.runScript = {'Load': self.runLoadScript, 'Registration': self.runRegisterScript, 
            'Analysis': self.runAnalysisScript}
        
        self.getAllScript()
        self.getAllPlugin()
        self.getAllWidgetView()
        
        self.actionSave.triggered.connect(self.saveData)
        self.actionClear_all.triggered.connect(self.clearAllData)
        self.mdiArea.subWindowActivated.connect(self.updateStatus)
        self.lastWindow = None
        
    
    def saveData(self):
        window = self.mdiArea.currentSubWindow()
        if not window:
            self.gui.showErrorMessage('Error', 'There\'re no data!')
        else:
            window = window.widget()
            window.save()
            data = window.getData()
            name, ok = QtGui.QInputDialog.getText(self, "Enter the name", 
                "Name:", QtGui.QLineEdit.Normal, window.getName())
            if ok and name:
                name = str(name)
                data.setName(name)
                dir = './Data/' + name
                db.saveMatData(dir, self.gui.dataModel, window.index)
                window.setWindowTitle(name)
    def getAllPlugin(self):
        self.pluginDir = gb.getAllGuiDir('Plugin')
        self.actionPlugin = [QtGui.QAction(gb.getGuiClass(x)().getName(), self, checkable = True,
            triggered = partial(self.enablePlugin, self.pluginDir.index(x))) for x in self.pluginDir]
        self.pluginGroup = QtGui.QActionGroup(self)
        for x in self.actionPlugin:
            self.pluginGroup.addAction(x)
            self.menuPlugin.addAction(x)
            if str(x.text()) == 'Null':
                x.setChecked(True)
                self.nullIndex = self.actionPlugin.index(x)
    def getAllWidgetView(self):
        self.viewDir = gb.getAllGuiDir('WidgetView')
        self.actionView = [QtGui.QAction(gb.getGuiClass(x)().getName(), self, checkable = True,
            triggered = partial(self.enableView, self.viewDir.index(x))) for x in self.viewDir]
        self.viewGroup = QtGui.QActionGroup(self)
        for x in self.actionView:
            self.viewGroup.addAction(x)
            self.menuWidget_View.addAction(x)
            if str(x.text()) == 'Result Image View':
                x.setChecked(True)
                self.resultIndex = self.actionView.index(x)
    def updateStatus(self):
        window = self.mdiArea.currentSubWindow()
        if not window:
            del self.lastWindow
            self.lastWindow = None
            return
        window = window.widget()
        if window == self.lastWindow:
            return
        if self.lastWindow:
            if self.lastWindow.isShow:
                self.lastWindow.save()
            else:
                del self.lastWindow
        
        self.lastWindow = window
        self.actionPlugin[window.widgetView.pluginIndex].setChecked(True)
        if type(window) is MdiChildRegistration:
            self.actionView[window.viewIndex].setChecked(True)
        
    def enablePlugin(self, index):
        # Need to check if the window can put it
        window = self.mdiArea.currentSubWindow()
        if not window:
            self.gui.showErrorMessage('Error', 'There\'re no data!')
        else:
            window = window.widget()
            window.save()
            
            window.setPlugin(gb.getGuiClass(self.pluginDir[index])(), index)
    def enableView(self, index):
        # Need to check if the window can put it
        window = self.mdiArea.currentSubWindow()
        if not window:
            self.gui.showErrorMessage('Error', 'There\'re no data!')
        else:
            window = window.widget()
            window.save()
            
            window.setView(gb.getGuiClass(self.viewDir[index]), index)
    def getAllScript(self):
        for key in self.menuScript.keys():
            dir = sb.getAllScriptDir(key)
            self.script[key] = [sb.runScriptFunc(x, self.gui) for x in dir]
            self.actionScript[key] = [QtGui.QAction(sb.getScriptName(x, self.gui), self, triggered = partial(self.runScript[key], dir.index(x))) for x in dir]
            for action in self.actionScript[key]:
                self.menuScript[key].addAction(action)
    def runLoadScript(self, index):
        temp = self.getMessageOnStatusBar()
        data = self.script['Load'][index]()
        if data:
            self.showMessageOnStatusBar("Loading...")
            self.addNewDataView(data)
        else:
            self.showMessageOnStatusBar(temp)
    def runRegisterScript(self, index):
        temp = self.getMessageOnStatusBar()
        data = self.script['Registration'][index]()
        if data:
            self.showMessageOnStatusBar("Registering...")
            self.addNewDataView(data)
        else:
            self.showMessageOnStatusBar(temp)
    def runAnalysisScript(self, index):
        # TO BE DONE
        data = self.script['Analysis'][index]()
        if data:
            self.showMessageOnStatusBar("Analysising...")
            index = self.gui.dataModel.append(data)
            child = self.createMdiChild(index)
            child.show()
    def addNewDataView(self, data):
        index = self.gui.dataModel.append(data)
        if type(data) is db.ResultData:
            child = self.createMdiChild(index, MdiChildRegistration)
        else:
            child = self.createMdiChild(index, MdiChildLoad)
        child.show()
    def createMdiChild(self, index, mdiChild):
        child = mdiChild(self.gui, index)
        self.mdiArea.addSubWindow(child)
        return child
    def showMessageOnStatusBar(self, text):
        self.msgLabel.setText(text)
    def getMessageOnStatusBar(self):
        return str(self.msgLabel.text())
    def clearAllData(self):
        self.showMessageOnStatusBar("Clearing...")
        self.mdiArea.closeAllSubWindows()
        self.gui.dataModel.data.clear()
        self.gui.showErrorMessage('Success', 'Sucessfully clear all the data!')
        self.showMessageOnStatusBar("")
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure to quit?", 
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
