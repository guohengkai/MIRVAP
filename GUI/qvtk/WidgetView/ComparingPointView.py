# -*- coding: utf-8 -*-
"""
Created on 2014-03-04

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.WidgetViewBase import RegistrationDataView
from MIRVAP.GUI.qvtk.Plugin.ContourViewPlugin import ContourViewPlugin

class ComparingPointView(RegistrationDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('fix'), widget)
        color = ((0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6))
        self.plugin = [ContourViewPlugin(), ContourViewPlugin()]
        self.plugin[0].enable(parent = self, color = color, dash = True, show = False)
        self.plugin[1].enable(parent = self, key = 'fix', show = False)
    def getName(self):
        return "Comparing PointSet View"
    def updateAfter(self, *arg):
        super(ComparingPointView, self).updateAfter(*arg)
        newMessage = "  (Fixed: Solid and light, Result: Dash and dark)"
        self.parent.gui.showMessageOnStatusBar(self.parent.gui.getMessageOnStatusBar() + newMessage)
