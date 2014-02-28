# -*- coding: utf-8 -*-
"""
Created on 2014-02-16

@author: Hengkai Guo
"""
# Operate on the image and get new feature or new data
class PluginBase(object):
    def getName(self):
        raise NotImplementedError('Method "getName" Not Impletemented!')
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
import sys, os, importlib
def getAllPluginDir():
    path = sys.argv[0]
    if os.path.isdir(path):
        pass
    elif os.path.isfile(path):
        path = os.path.dirname(path)
        
    path += '/GUI/Plugin/'
    
    dir = os.listdir(path)
    dir = [str('MIRVAP.GUI.Plugin.' + x[:-3]) for x in dir if x.endswith('.py') and not x.startswith('_')]
    
    return dir
def getPluginInstance(dir):
    mod = importlib.import_module(dir)
    name = dir.split('.')[-1]
    cl = getattr(mod, name)
    ins = cl()
    return ins
