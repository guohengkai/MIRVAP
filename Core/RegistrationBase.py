# -*- coding: utf-8 -*-
"""
Created on 2014-02-07

@author: Hengkai Guo
"""

from ScriptBase import ScriptBase
import MIRVAP.GUI.PyQtGui as gui
# Input two images, output one image
class RegistrationBase(ScriptBase):
    def __init__(self, gui):
        super(RegistrationBase, self).__init__(gui)
        
    def run(self, *args, **kwargs):
        indexes = self.gui.getDataIndexes()
        if indexes:
            if len(indexes) == 2:
                resultData = self.register(self.gui.dataModel[indexes[0]], self.gui.dataModel[indexes[1]])        
                resultData.addDetail('fix', indexes[0])
                resultData.addDetail('move', indexes[1])
                return resultData
            
    def register(self, fixedData, movingData):
        raise NotImplementedError('Method "register" Not Impletemented!')
