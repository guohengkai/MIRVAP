# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

from DataModel import DataModel
import ClipPlugin, CVModelLevelsetPlugin, ContourPlugin, ContourViewPlugin, NullPlugin
import ComparingPointView, ComparingSurfaceView, FixedImageView, MovingImageView, ResultImageView, SurfaceView

class GuiControllerBase(object):
    def __init__(self):
        self.dataModel = DataModel()
    def startApplication(self):
        raise NotImplementedError('Method "startApplication" Not Impletemented!')

import sys, os, importlib
def getAllGuiDir(dir):
    if dir == 'Plugin':
        list = ['ClipPlugin', 'CVModelLevelsetPlugin', 'ContourPlugin', 'ContourViewPlugin', 'NullPlugin']
    else:
        list = ['ComparingPointView', 'ComparingSurfaceView', 'FixedImageView', 'MovingImageView', 'ResultImageView', 'SurfaceView']
    
    return list
def getGuiClass(dir):
    mod = importlib.import_module(dir)
    name = dir.split('.')[-1]
    cl = getattr(mod, name)
    return cl
