# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

import sys, os, importlib

class ScriptBase(object):
    def __init__(self, gui):
        self.gui = gui
        
    def run(self, *args, **kwargs):
        raise NotImplementedError('Method "run" Not Impletemented!')
    def setCallback(self, func):
        self.callback = func
    def getName(self):
        raise NotImplementedError('Method "getName" Not Impletemented!')

def getScriptInstance(dir, gui):
    mod = importlib.import_module(dir)
    name = dir.split('.')[-1]
    cl = getattr(mod, name)
    ins = cl(gui)
    return ins
def runScriptFunc(dir, gui, callback = None):
    ins = getScriptInstance(dir, gui)
    if callback:
        ins.setCallback(callback)
    return ins.run
def getScriptName(dir, gui):
    return getScriptInstance(dir, gui).getName()
def getAllScriptDir(dir):
    if dir == 'Load':
        list = ['LoadDicomDir', 'LoadDicomFile', 'LoadMatFile']
    elif dir == 'Save':
        list = ['SaveMatFile']
    else:
        list = ['IcpPointsetRegistration']
    return list

