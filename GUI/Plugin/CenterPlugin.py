# -*- coding: utf-8 -*-
"""
Created on 2014-02-26

@author: Hengkai Guo
"""

from ContourPlugin import ContourPlugin

class CenterPlugin(ContourPlugin):
    def __init__(self):
        super(CenterPlugin, self).__init__()
        self.key = 'Centerline'
