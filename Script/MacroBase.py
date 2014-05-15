# -*- coding: utf-8 -*-
"""
Created on 2014-04-26

@author: Hengkai Guo
"""

from MIRVAP.Core.ScriptBase import ScriptBase

class MacroBase(ScriptBase):
    def __init__(self, gui):
        super(MacroBase, self).__init__(gui)
    
    def run(self, window = None):
        dataset = self.load()
        self.process(dataset)
        if self.gui:
            self.gui.showErrorMessage('Success', 'Test sucessfully!')
        else:
            print 'Test sucessfully!'
    def load(self):
        raise NotImplementedError('Method "load" Not Impletemented!')
    def process(self, dataset):
        raise NotImplementedError('Method "process" Not Impletemented!')
        
