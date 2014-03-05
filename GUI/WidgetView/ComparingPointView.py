# -*- coding: utf-8 -*-
"""
Created on 2014-03-04

@author: Hengkai Guo
"""

from MIRVAP.Core.WidgetViewBase import RegistrationDataView
from MIRVAP.GUI.Plugin.ContourViewPlugin import ContourViewPlugin
from MIRVAP.GUI.Plugin.CenterViewPlugin import CenterViewPlugin

class ComparingPointView(RegistrationDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('fix'), widget)
        color = ((0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6))
        self.plugin = [ContourViewPlugin(), ContourViewPlugin(), CenterViewPlugin(), CenterViewPlugin()]
        self.plugin[0].enable(parent = self, color = color, dash = True)
        self.plugin[1].enable(parent = self, key = 'fix')
        self.plugin[2].enable(parent = self, color = color)
        self.plugin[3].enable(parent = self, key = 'fix')
    def getName(self):
        return "Comparing PointSet View"
