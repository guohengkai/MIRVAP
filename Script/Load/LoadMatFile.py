# -*- coding: utf-8 -*-
"""
Created on 2014-02-05

@author: Hengkai Guo
"""

import MIRVAP.Core.DataBase as db
from MIRVAP.Core.LoadBase import LoadBase

class LoadMatFile(LoadBase):
    def __init__(self, gui):
        super(LoadMatFile, self).__init__(gui)
    def getName(self):
        return 'Load from mat files'
    def getLoadParameters(self):
        pass
    def load(self, dir):
        data, info, point = db.loadMatData(dir[0])
        # Need to add registration data reader
        fileData = db.BasicData(data, info, point)
        return fileData
        
if __name__ == "__main__":
    from MIRVAP.Test.TestGui import TestGui
    load = LoadMatFile(TestGui())
    image = load.load()
    print image.getData().shape
    print image.getResolution()
    print image.getModality()
