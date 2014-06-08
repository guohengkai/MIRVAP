# -*- coding: utf-8 -*-
"""
Created on 2014-06-07

@author: Hengkai Guo
"""
import numpy as npy
import sys

from ContourPlugin import ContourPlugin
from util.acontour.ac_segmentation import ac_segmentation
from util.acontour.ac_function import ac_area
from util.PluginUtil import calCentroidFromContour

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
            
            image = self.parent.parent.getData().getData()[npy.round(point_array[0, self.parent.view]), :, :].transpose().copy()
            image = (image - npy.min(image)) / (npy.max(image) - npy.min(image)) * 255
            result = ac_segmentation(point_array[0, :2], image)
            
            # Save all the new points
            point_array = npy.insert(result.transpose(), self.parent.view, point_array[0, self.parent.view], axis = 1) * space
            self.contourRep[self.currentContour].ClearAllNodes()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
            self.parent.render_window.Render()
            return
        if ch == 't' or ch == 'T':
            th = 1.5
            resolution = self.parent.parent.getData().getResolution().tolist()
            
            space = self.parent.space
            if len(space) == 2:
                space += [1]
            point_array = self.getAllPoint() / space
            if point_array.shape[0] == 0:
                return
            
            if self.currentContour == 0:
                delta = -1
            else:
                delta = 1
            z = int(point_array[0, self.parent.view] + 0.5)
            frame_size = self.parent.parent.getData().getData()[z + delta, :, :].transpose().shape
            temp = self.parent.parent.getData().getPointSet('Contour')
            last_points = temp[(npy.round(temp[:, 2]) == z + delta) & (npy.round(temp[:, -1]) == self.currentContour)]
            a1 = ac_area(last_points[:, :2].transpose(), frame_size)
            a2 = ac_area(point_array[:, :2].transpose(), frame_size)
            rate = a2 * 1.0 / a1
            print a1, a2, rate
            if rate >= 1.5 or rate <= 0.7:
                point_array = last_points[:, :2]
                point_array = npy.insert(point_array, self.parent.view, z, axis = 1) * space
                self.contourRep[self.currentContour].ClearAllNodes()
                for i in range(point_array.shape[0]):
                    self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
                self.parent.render_window.Render()
            
        if ch == 's' or ch == 'S':
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
            print bottom, bif, up1, up2
            
            self.autoDetectContour(point_vital[0], 0, bottom, bif, 1)
            self.autoDetectContour(point_vital[1], 1, up1, bif, -1)
            self.autoDetectContour(point_vital[2], 2, up2, bif, -1)
            
            self.parent.render_window.Render()
            return
        super(CVModelLevelsetPlugin, self).KeyPressCallback(obj, event)
    def autoDetectContour(self, point, cnt, start, end, delta):
        points = point[npy.round(point[:, 2]) == start]
        if points is None:
            return
        points = points[:, :-2]
        count = 0
        for i in range(start + delta, end + delta, delta):
            center = calCentroidFromContour(points).reshape(2)
            image = self.parent.parent.getData().getData()[i, :, :].transpose().copy()
            image = (image - npy.min(image)) / (npy.max(image) - npy.min(image)) * 255
            result = ac_segmentation(center, image)
            
            a1 = ac_area(points.transpose(), image.shape)
            a2 = ac_area(result, image.shape)
            rate = a2 * 1.0 / a1
            if rate >= min(1.5 + count * 0.2, 2.1) or rate <= 0.7:
                temp_array = points.copy()
                if cnt != 1 and rate > 0.7:
                    count += 1
            else:
                temp_array = result.transpose().copy()
                count = 0
            points = temp_array.copy()
            
            temp_array = npy.insert(temp_array, [temp_array.shape[1]], npy.ones((temp_array.shape[0], 1), int) * i, axis = 1)
            self.parent.parent.getData().pointSet.setSlicePoint('Contour', temp_array, 2, i, cnt)
            
            sys.stdout.write(str(i) + ',')
            sys.stdout.flush()
        print ' '
    def getName(self):
        return "C-V Model Contour Detector"
