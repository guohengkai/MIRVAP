# -*- coding: utf-8 -*-
"""
Created on 2014-08-10

@author: Hengkai Guo
"""
import numpy as npy
import sys

from ContourPlugin import ContourPlugin
from util.PluginUtil import calCentroidFromContour
from util.MCPUtil import calMinimumCostPathCenterline

class MCPCenterlinePlugin(ContourPlugin):
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            # Get the input information (begin, end, bifurcation)
            temp = self.parent.parent.getData().getPointSet('Contour')
            point_vital = [0] * 3
            for i in range(3):
                point_vital[i] = temp[npy.round(temp[:, -1]) == i].copy()
                if point_vital[i].shape[0] == 0:
                    return
            
            bottom = int(npy.round(npy.min(point_vital[0][:, 2])))
            up1 = int(npy.round(npy.max(point_vital[1][:, 2])))
            up2 = int(npy.round(npy.max(point_vital[2][:, 2])))
            print bottom, up1, up2
            
            center_bottom = npy.zeros([3], dtype = npy.float32)
            center_up1 = npy.zeros([3], dtype = npy.float32)
            center_up2 = npy.zeros([3], dtype = npy.float32)
            center_bottom[:2] = calCentroidFromContour(point_vital[0][npy.round(point_vital[0][:, 2]) == bottom][:, :2]).reshape(2)
            center_up1[:2] = calCentroidFromContour(point_vital[1][npy.round(point_vital[1][:, 2]) == up1][:, :2]).reshape(2)
            center_up2[:2] = calCentroidFromContour(point_vital[2][npy.round(point_vital[2][:, 2]) == up2][:, :2]).reshape(2)
            center_bottom[-1] = bottom
            center_up1[-1] = up1
            center_up2[-1] = up2
            
            result = calMinimumCostPathCenterline(center_bottom, center_up1, center_up2, self.parent.parent.getData().getData(), self.parent.parent.getData().getResolution())
            self.parent.parent.getData().pointSet.data['Centerline'] = result
            
            self.parent.render_window.Render()
            return
        if ch == 't' or ch == 'T':
            # For test
            self.parent.render_window.Render()
            return
        super(MCPCenterlinePlugin, self).KeyPressCallback(obj, event)
    def getName(self):
        return "Minimum Cost Path Centerline Detector"
