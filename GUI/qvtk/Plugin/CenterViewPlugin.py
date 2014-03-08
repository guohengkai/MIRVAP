# -*- coding: utf-8 -*-
"""
Created on 2014-02-26

@author: Hengkai Guo
"""

from CenterPlugin import CenterPlugin

class CenterViewPlugin(CenterPlugin):
    def __init__(self):
        super(CenterViewPlugin, self).__init__()
        self.editable = False
