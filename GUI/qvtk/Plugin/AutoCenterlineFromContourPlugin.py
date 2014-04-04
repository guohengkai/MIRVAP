# -*- coding: utf-8 -*-
"""
Created on 2014-04-04

@author: Hengkai Guo
"""
import cv
import numpy as npy

from ContourPlugin import ContourPlugin

# Only in z direction
class AutoCenterlineFromContourPlugin(ContourPlugin):
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
            bif = int(npy.round(npy.max(point_vital[0][:, 2])))
            up1 = int(npy.round(npy.max(point_vital[1][:, 2])))
            up2 = int(npy.round(npy.max(point_vital[2][:, 2])))
            print bottom, bif
            print up1, up2
            
            
            
            self.parent.render_window.Render()
            return
        super(AutoCenterlineFromContourPlugin, self).KeyPressCallback(obj, event)
    
    def getName(self):
        return "Auto Centerline From Contour"
        
