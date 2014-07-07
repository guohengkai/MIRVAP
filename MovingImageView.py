# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from WidgetViewBase import RegistrationDataView
from ContourViewPlugin import ContourViewPlugin

class MovingImageView(RegistrationDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('move'), widget)
        self.plugin = [ContourViewPlugin()]
        self.plugin[0].enable(parent = self, key = 'move', show = False)
    def getName(self):
        return "Moving Image View"
