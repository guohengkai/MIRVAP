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
            point_array_result = self.parent.parent.getData().pointSet
            point_data_result = npy.array(point_array_result.getData('Contour'))
            center_data = npy.array([[-1, -1, -1, -1]])
            if point_data_result is None or not point_data_result.shape[0]:
                return
            zmin = int(npy.min(point_data_result[:, 2]) + 0.5)
            zmax = int(npy.max(point_data_result[:, 2]) + 0.5)
            for cnt in range(3):
                point_result = point_data_result[npy.where(npy.round(point_data_result[:, -1]) == cnt)]
                if not point_result.shape[0]:
                    continue
                    
                for i in range(zmin, zmax + 1):
                    data = point_result[npy.where(npy.round(point_result[:, 2]) == i)]
                    if data is not None:
                        if data.shape[0] == 0:
                            continue
                        center_data = npy.append(center_data, npy.mean(data, axis = 0).reshape(1, -1), axis = 0)
                        
            point_array_result.data['Centerline'] = center_data
            self.parent.updateAfter()
            self.parent.render_window.Render()
            return
        super(AutoCenterlineFromContourPlugin, self).KeyPressCallback(obj, event)
    
    def getName(self):
        return "Auto Centerline From Contour"
        
