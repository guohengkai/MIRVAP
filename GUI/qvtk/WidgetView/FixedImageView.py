# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.WidgetViewBase import RegistrationDataView
from MIRVAP.GUI.qvtk.Plugin.ContourViewPlugin import ContourViewPlugin

class FixedImageView(RegistrationDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('fix'), widget)
        self.plugin = [ContourViewPlugin()]
        self.plugin[0].enable(parent = self, key = 'fix', show = False)
    def getName(self):
        return "Fixed Image View"
