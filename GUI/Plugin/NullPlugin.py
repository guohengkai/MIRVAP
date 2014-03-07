# -*- coding: utf-8 -*-
"""
Created on 2014-02-17

@author: Hengkai Guo
"""

from MIRVAP.Core.PluginBase import PluginBase

class NullPlugin(PluginBase):
    def getName(self):
        return 'Null'
    def updateAfter(self, view, slice, *arg):
        pass
