# -*- coding: utf-8 -*-
"""
Created on 2014-02-01

@author: Hengkai Guo
"""


from PyQt4 import QtCore, QtGui
from Ui_MainWindow import Ui_MainWindow
from MdiChild import MdiChildLoad#, MdiChildRegistration
import MIRVAP.Core.DataBase as db
import MIRVAP.Core.ScriptBase as sb
import MIRVAP.Core.PluginBase as pb
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
        
        self.actionSave.triggered.connect(self.saveData)
        self.mdiArea.subWindowActivated.connect(self.updateStatus)
        self.lastWindow = None
        
    
    def saveData(self):
        window = self.mdiArea.currentSubWindow()
        if not window:
            self.showErrorMessage('Error', 'There\'re no data!')
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
                db.saveMatData(dir, data)
                window.setWindowTitle(name)
    def getAllPlugin(self):
        self.pluginDir = pb.getAllPluginDir()
        self.actionPlugin = [QtGui.QAction(pb.getPluginInstance(x).getName(), self, checkable = True,
            triggered = partial(self.enablePlugin, self.pluginDir.index(x))) for x in self.pluginDir]
        self.pluginGroup = QtGui.QActionGroup(self)
        for x in self.actionPlugin:
            self.pluginGroup.addAction(x)
            self.menuPlugin.addAction(x)
            if str(x.text()) == 'Null':
                x.setChecked(True)
                self.nullIndex = self.actionPlugin.index(x)
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
        
    def enablePlugin(self, index):
        window = self.mdiArea.currentSubWindow()
        if not window:
            self.showErrorMessage('Error', 'There\'re no data!')
        else:
            window = window.widget()
            window.save()
            
            window.setPlugin(pb.getPluginInstance(self.pluginDir[index]), index)
            
    def getAllScript(self):
        for key in self.menuScript.keys():
            dir = sb.getAllScriptDir(key)
            self.script[key] = [sb.runScriptFunc(x, self.gui) for x in dir]
            self.actionScript[key] = [QtGui.QAction(sb.getScriptName(x, self.gui), self, triggered = partial(self.runScript[key], dir.index(x))) for x in dir]
            for action in self.actionScript[key]:
                self.menuScript[key].addAction(action)
    def runLoadScript(self, index):
        temp = self.getMessageOnStatusBar()
        self.showMessageOnStatusBar("Loading...")
        data = self.script['Load'][index]()
        if data:
            self.addNewDataView(data)
        else:
            self.showMessageOnStatusBar(temp)
    def runRegisterScript(self, index):
        # TO BE DONE
        data = self.script['Registration'][index]()
        if data:
            self.showMessageOnStatusBar("Registering...")
            index = self.gui.dataModel.append(data)
            child = self.createMdiChild(index, MdiChildRegistration)
            child.show()
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
        child = self.createMdiChild(index, MdiChildLoad)
        child.show()
    def createMdiChild(self, index, mdiChild):
        child = mdiChild(self.gui, index)
        self.mdiArea.addSubWindow(child)
        return child
        
    def getFileNames(self, *args):
        # The argument need to be setted
        temp = QtGui.QFileDialog.getOpenFileNames()
        fileNames = map(str, temp)
        return fileNames
    def getDataIndexes(self):
        indexList = map(int, self.gui.dataModel.getIndexList())
        names = {}
        for index in indexList:
            name = self.gui.dataModel[index].getName()
            if not name:
                name = 'Data %d' % index
            names[name] = index
        items = names.keys()
        item, ok = QtGui.QInputDialog.getItem(self, "Select the fixed image", 
            "Fixed image:", items, 0, False)
        if ok and item:
            fixedIndex = names[item]
            items.remove(item)
            item, ok = QtGui.QInputDialog.getItem(self, "Select the moving image", 
                "Moving image:", items, 0, False)
            if ok and item:
                movingIndex = names[item]
                return (fixedIndex, movingIndex)
    def showErrorMessage(self, title, message):
        QtGui.QMessageBox.information(self, title, message)
    def showMessageOnStatusBar(self, text):
        # Need to be changed to label in statusbar
        #self.statusbar.showMessage(text)
        self.msgLabel.setText(text)
    def getMessageOnStatusBar(self):
        #return str(self.statusbar.currentMessage())
        return str(self.msgLabel.text())
        
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure to quit?", 
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
