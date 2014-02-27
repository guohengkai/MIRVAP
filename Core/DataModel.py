# -*- coding: utf-8 -*-
"""
Created on 2014-02-05

@author: Hengkai Guo
"""

import DataBase as db
class DataModel(object):
    def __init__(self):
        self.data = {}
    def __getitem__(self, index):
        return self.data.get(index, None)
    
    def getIndexList(self):
        return sorted(list(self.data.keys()))
    def getCount(self):
        return len(self.data)
    def append(self, data):
        if self.data:
            index = max(list(self.data.keys())) + 1
        else:
            index = 0
        self.data[index] = data
        return index
    def remove(self, index):
        if self[index]:
            del self.data[index]
        
