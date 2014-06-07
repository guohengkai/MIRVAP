# -*- coding: utf-8 -*-
"""
Created on 2014-06-07

@author: Hengkai Guo
"""
import cv
import numpy as npy

from ContourPlugin import ContourPlugin
from util.acontour.ac_segmentation import ac_segmentation

class CVModelLevelsetPlugin(ContourPlugin):
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            # Get all the points
            space = self.parent.space
            if len(space) == 2:
                space += [1]
            point_array = self.getAllPoint() / space
            if point_array.shape[0] != 1:
                return
            
            image = self.parent.parent.getData().getData()[npy.round(point_array[0, self.parent.view]), :, :].transpose()
            result = ac_segmentation(point_array[0, :2], image)
            
            # Save all the new points
            point_array = npy.insert(result.transpose(), self.parent.view, point_array[0, self.parent.view], axis = 1) * space
            self.contourRep[self.currentContour].ClearAllNodes()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
            self.parent.render_window.Render()
            return
        if ch == 'Up' or ch == 'Down':
            
            return
        super(CVModelLevelsetPlugin, self).KeyPressCallback(obj, event)
        
    def getName(self):
        return "C-V Model Contour Detector"
