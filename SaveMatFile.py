# -*- coding: utf-8 -*-
"""
Created on 2014-03-05

@author: Hengkai Guo
"""

import DataBase as db
from SaveBase import SaveBase

class SaveMatFile(SaveBase):
    def getName(self):
        return 'Save to mat files'
    def save(self, window, data):
        name, ok = self.gui.getInputName(window)
        if ok and name:
            name = str(name)
            data.setName(name)
            dir = './Data/' + name
            db.saveMatData(dir, self.gui.dataModel, window.index)
            window.setWindowTitle(name)
            return True
