# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from MIRVAP.Script.LoadBase import LoadBase

class LoadDataModel(LoadBase):
    def __init__(self, gui):
        super(LoadDataModel, self).__init__(gui)
    def getName(self):
        return 'Reload from memory'
    def run(self, *args, **kwargs):
        index = self.gui.getReloadDataIndex()
        if index is not None:
            return self.load(index)
    def load(self, index):
        return self.gui.dataModel[index]
