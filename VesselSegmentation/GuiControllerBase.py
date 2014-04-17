# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""

from DataModel import DataModel

class GuiControllerBase(object):
    def __init__(self):
        self.dataModel = DataModel()
    def startApplication(self):
        raise NotImplementedError('Method "startApplication" Not Impletemented!')