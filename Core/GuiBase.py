# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

from DataModel import DataModel

class GuiBase(object):
    def __init__(self):
        self.dataModel = DataModel()
    def startApplication(self):
        raise NotImplementedError('Method "startApplication" Not Impletemented!')

import sys, os, importlib
def getAllGuiDir(dir):
    path = sys.argv[0]
    if os.path.isdir(path):
        pass
    elif os.path.isfile(path):
        path = os.path.dirname(path)
        
    path += '/GUI/' + dir + '/'
    
    list = os.listdir(path)
    list = [str('MIRVAP.GUI.' + dir + '.' + x[:-3]) for x in list if x.endswith('.py') and not x.startswith('_')]
    
    return list
def getGuiClass(dir):
    mod = importlib.import_module(dir)
    name = dir.split('.')[-1]
    cl = getattr(mod, name)
    return cl
