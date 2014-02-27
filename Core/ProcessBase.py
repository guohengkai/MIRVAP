# -*- coding: utf-8 -*-
"""
Created on 2014-02-20

@author: Hengkai Guo
"""

from ScriptBase import ScriptBase
import MIRVAP.GUI.PyQtGui as gui
# Input one image, output one image
class ProcessBase(ScriptBase):
    def __init__(self, gui):
        super(ProcessBase, self).__init__(gui)
        
    def run(self, *args, **kwargs):
        # TO BE DONE
        pass
            
    def process(self, data):
        raise NotImplementedError('Method "process" Not Impletemented!')
