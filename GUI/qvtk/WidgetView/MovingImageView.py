# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.WidgetViewBase import RegistrationDataView
from MIRVAP.GUI.qvtk.Plugin.ContourViewPlugin import ContourViewPlugin
from MIRVAP.GUI.qvtk.Plugin.CenterViewPlugin import CenterViewPlugin

class MovingImageView(RegistrationDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('move'), widget)
        self.plugin = [ContourViewPlugin(), CenterViewPlugin()]
        self.plugin[0].enable(parent = self, key = 'move', show = False)
        self.plugin[1].enable(parent = self, key = 'move', show = False)
    def getName(self):
        return "Moving Image View"
