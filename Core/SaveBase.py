# -*- coding: utf-8 -*-
"""
Created on 2014-03-05

@author: Hengkai Guo
"""

from ScriptBase import ScriptBase
import MIRVAP.GUI.PyQtGui as gui

class SaveBase(ScriptBase):
    def __init__(self, gui):
        super(SaveBase, self).__init__(gui)
    
    def run(self, window):
        window.save()
        data = window.getData()
        self.save(window, data)
        
    def save(self, window, data):
        raise NotImplementedError('Method "save" Not Impletemented!')
        
