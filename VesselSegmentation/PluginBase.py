# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""

# Operate on the image and get new feature or new data
class PluginBase(object):
    def getName(self):
        raise NotImplementedError('Method "getName" Not Impletemented!')
    def getHelpInfo():
        raise NotImplementedError('Method "getHelpInfo" Not Impletemented!')
    def MouseMoveCallback(self, obj, event):
        pass
    def LeftButtonReleaseCallback(self, obj, event):
        pass
    def KeyPressCallback(self, obj, event):
        pass
    def LeftButtonPressCallback(self, obj, event):
        pass
    def MiddleButtonPressCallback(self, obj, event):
        pass        
    def RightButtonPressCallback(self, obj, event):
        pass
    def RightButtonReleaseCallback(self, obj, event):
        pass
    def updateAfter(self, view, slice, *arg):
        pass
    def updateBefore(self, view, slice, *arg):
        pass
    def save(self):
        pass
    def enable(self, parent):
        pass
    def disable(self):
        pass
        
