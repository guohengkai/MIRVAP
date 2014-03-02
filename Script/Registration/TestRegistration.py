# -*- coding: utf-8 -*-
"""
Created on 2014-02-28

@author: Hengkai Guo
"""

from MIRVAP.Core.RegistrationBase import RegistrationBase

class TestRegistration(RegistrationBase):
    def __init__(self, gui):
        super(TestRegistration, self).__init__(gui)
    def getName(self):
        return 'Doing nothing'
    def register(self, fixedData, movingData):
        return fixedData.getData()
        
