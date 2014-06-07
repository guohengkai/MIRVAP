# -*- coding: utf-8 -*-
"""
Created on 2014-06-06

@author: Hengkai Guo
"""
import cv
import numpy as npy

from ContourPlugin import ContourPlugin

class NoiseContourPlugin(ContourPlugin):
    def __init__(self):
        super(NoiseContourPlugin, self).__init__()
        self.sd = 0.2
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            print self.sd
            # Get all the points
            space = self.parent.space
            if len(space) == 2:
                space += [1]
            point_array = self.getAllPoint() / space
            if point_array.shape[0] == 0:
                return
            
            point_array[:, :3] = AddNoise(point_array[:, :3], self.sd)
            # Save all the new points
            point_array[:, :3] *= space
            self.contourRep[self.currentContour].ClearAllNodes()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
            self.parent.render_window.Render()
            return
        if ch == 'Up' or ch == 'Down':
            if ch == 'Up':
                if self.sd < 3:
                    self.sd += 0.2
            else:
                if self.sd > 0:
                    self.sd -= 0.2
            return
        super(NoiseContourPlugin, self).KeyPressCallback(obj, event)
        
    def getName(self):
        return "Noise Contour Detector"
        
def AddNoise(points, sd):
    result_point = points.copy()
    if sd > 0:
        noise = npy.matlib.randn(result_point.shape[0], 2) * sd
        result_point[:, :2] += noise
    return result_point
