# -*- coding: utf-8 -*-
"""
Created on 2014-08-07

@author: Hengkai Guo
"""

import MIRVAP.Core.DataBase as db
from MIRVAP.Script.LoadBase import LoadBase

class LoadRawFile(LoadBase):
    def __init__(self, gui):
        super(LoadRawFile, self).__init__(gui)
    def getName(self):
        return 'Load from raw file'
    def getLoadParameters(self):
        title = 'Open Raw Data'
        dir = 'Data'
        filter = 'Raw Files(*.mhd)'
        return title, dir, filter
    def load(self, dir):
        result = []
        for name in dir:
            data, info, point = db.loadRawData(name)
            import numpy
            print numpy.sum(data)
            fileData = db.BasicData(data, info, point)
            result.append(fileData)
        return result
