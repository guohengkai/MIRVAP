# -*- coding: utf-8 -*-
"""
Created on 2014-02-05

@author: Hengkai Guo
"""

import MIRVAP.Core.DataBase as db
from MIRVAP.Script.LoadBase import LoadBase

class LoadMatFile(LoadBase):
    def __init__(self, gui):
        super(LoadMatFile, self).__init__(gui)
    def getName(self):
        return 'Load from mat files'
    def getLoadParameters(self):
        title = 'Open Matlab Data'
        dir = 'Data'
        filter = 'Mat Files(*.mat)'
        return title, dir, filter
    def load(self, dir):
        data, info, point = db.loadMatData(dir[0], self.gui.dataModel)
        if info.getData('fix') is not None:
            fileData = db.ResultData(data, info, point)
        else:
            fileData = db.BasicData(data, info, point)
        return fileData
