# -*- coding: utf-8 -*-
"""
Created on 2014-03-04

@author: Hengkai Guo
"""

from MIRVAP.Core.WidgetViewBase import SingleDataView
from MIRVAP.GUI.Plugin.ContourViewPlugin import ContourViewPlugin

class ComparingPointView(SingleDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('fix'), widget)
        self.plugin = [ContourViewPlugin(), ContourViewPlugin()]
        self.plugin[0].enable(self)
        self.plugin[1].enable(self, 'fix')
    def getName(self):
        return "Comparing PointSet View"
