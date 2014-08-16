# -*- coding: utf-8 -*-
"""
Created on 2014-08-16

@author: Hengkai Guo
"""

from ContourPlugin import ContourPlugin

class MaskPlugin(ContourPlugin):
    def __init__(self):
        super(MaskPlugin, self).__init__()
        self.key = 'Mask'
