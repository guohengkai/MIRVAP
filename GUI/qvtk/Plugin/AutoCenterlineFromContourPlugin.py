# -*- coding: utf-8 -*-
"""
Created on 2014-04-04

@author: Hengkai Guo
"""

import numpy as npy

from ContourPlugin import ContourPlugin
from util.PluginUtil import calCenterlineFromContour, calCentroidFromContour, calIntensityCentroidFromContour, calCenterFromContour

# Only in z direction
class AutoCenterlineFromContourPlugin(ContourPlugin):
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            point_array_result = self.parent.parent.getData().pointSet
            func = None
            #func = calIntensityCentroidFromContour
            #func = calCenterFromContour
            center_data = calCenterlineFromContour(point_array_result.data, func = func, image = self.parent.parent.getData().getData())            
            point_array_result.data['Centerline'] = center_data
            self.parent.updateAfter()
            self.parent.render_window.Render()
            return
        super(AutoCenterlineFromContourPlugin, self).KeyPressCallback(obj, event)
    
    def getName(self):
        return "Auto Centerline From Contour"
