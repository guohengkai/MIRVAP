# -*- coding: utf-8 -*-
"""
Created on 2014-02-02

@author: Hengkai Guo
"""

from ScriptBase import ScriptBase
import MIRVAP.GUI.PyQtGui as gui
# Input nothing, output one image
class LoadBase(ScriptBase):
    def __init__(self, gui):
        super(LoadBase, self).__init__(gui)
        
    def run(self, *args, **kwargs):
        dir = self.gui.getFileNames(self.getLoadParameters())
        if dir:
            return self.load(dir)
        
    def load(self, dir):
        raise NotImplementedError('Method "load" Not Impletemented!')
    def getLoadParameters(self):
        raise NotImplementedError('Method "getLoadParameters" Not Impletemented!')
        