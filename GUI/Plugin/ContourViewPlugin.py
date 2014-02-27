# -*- coding: utf-8 -*-
"""
Created on 2014-02-17

@author: Hengkai Guo
"""

from ContourPlugin import ContourPlugin

class ContourViewPlugin(ContourPlugin):
    def __init__(self):
        super(ContourViewPlugin, self).__init__()
        self.editable = False
