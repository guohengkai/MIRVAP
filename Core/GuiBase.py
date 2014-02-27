# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

from DataModel import DataModel
class GuiBase(object):
    def __init__(self):
        self.dataModel = DataModel()
        
    def getFileNames(self, *args):
        raise NotImplementedError('Method "getFileNames" Not Impletemented!')
    def getDataIndexes(self):
        raise NotImplementedError('Method "getDataIndexes" Not Impletemented!')
    def showErrorMessage(self, title, message):
        raise NotImplementedError('Method "showErrorMessage" Not Impletemented!')    
    def showMessageOnStatusBar(self, text):
        raise NotImplementedError('Method "showMessageOnStatusBar" Not Impletemented!')
    def getMessageOnStatusBar(self):
        raise NotImplementedError('Method "getMessageOnStatusBar" Not Impletemented!')   
    def addNewDataView(self, data):
        raise NotImplementedError('Method "addNewDataView" Not Impletemented!')   
    def startApplication(self):
        raise NotImplementedError('Method "startApplication" Not Impletemented!')
