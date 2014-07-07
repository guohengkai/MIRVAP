# -*- coding: utf-8 -*-
"""
Created on 2014-02-05

@author: Hengkai Guo
"""

import DataBase as db
from LoadBase import LoadBase

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
        result = []
        for name in dir:
            data, info, point = db.loadMatData(name, self.gui.dataModel)
            if info.getData('fix') is not None:
                fileData = db.ResultData(data, info, point)
            else:
                fileData = db.BasicData(data, info, point)
            result.append(fileData)
        return result
