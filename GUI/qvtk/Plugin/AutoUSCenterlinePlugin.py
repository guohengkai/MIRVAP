# -*- coding: utf-8 -*-
"""
Created on 2014-08-10

@author: Hengkai Guo
"""

import numpy as npy

from ContourPlugin import ContourPlugin
import util.USUtil as util

class AutoUSCenterlinePlugin(ContourPlugin):
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            # Get the resolution of image
            space = self.parent.space
            if len(space) == 2:
                space += [1]
                
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
            
            self.autoDetectContour(point_vital, 0, bottom, bif, space)
            self.autoDetectContour(point_vital, 1, up1, bif, space)
            self.autoDetectContour(point_vital, 2, up2, bif, space)
            
            self.parent.render_window.Render()
            return
        if ch in ['t', 'T']:
            space = self.parent.space
            if len(space) == 2:
                space += [1]
            point_array = self.getAllPoint() / space
            if point_array.shape[0] == 0:
                return
                
            temp_array = npy.delete(point_array, 2, axis = 1)
            # Get the 2D image
            image = self.parent.parent.getData().getData()[npy.round(point_array[0, self.parent.view]), :, :].transpose()
            
            # Ellipse fitting
            center, diameter, angle = util.ellipseFitting(temp_array)
            
            sigmaMin = 4
            n = 1000
            d = 1.0 / self.parent.parent.getData().getResolution()[-1]
            #th = util.getThreshold(image, center, d, space[0:2], sigmaMin)
            th, gradient_img = util.getGradientThresholdAndImage(image, center, d, space[0:2])
            resultPoints, distance = util.getRayPoints(gradient_img, center, n, th)
            h, w = image.shape
            prunedPoints = util.finePrune(resultPoints, distance, center, diameter, angle, h, w)
#            center, diameter, angle = util.ransac(prunedPoints, util.EllipseLeastSquaresModel(),
#                50, 200, 50, 800)
#            temp_array = util.getPointsFromEllipse(center, diameter, angle, 20)
            temp_array = prunedPoints
            
            # Save all the new points
            point_array = npy.insert(temp_array, self.parent.view, point_array[0, self.parent.view], axis = 1) * space
            self.contourRep[self.currentContour].ClearAllNodes()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
            self.parent.render_window.Render()
            
            return
        if ch in ['e', 'E']:
            space = self.parent.space
            if len(space) == 2:
                space += [1]
            point_array = self.getAllPoint() / space
            if point_array.shape[0] == 0:
                return
                
            temp_array = npy.delete(point_array, 2, axis = 1)
            center, diameter, angle = util.ellipseFitting(temp_array)
            #center, diameter, angle = util.ransac(temp_array, util.EllipseLeastSquaresModel(), 50, 200, 50, 800)
            temp_array = util.getPointsFromEllipse(center, diameter, angle, 20)
            
            point_array = npy.insert(temp_array, self.parent.view, point_array[0, self.parent.view], axis = 1) * space
            self.contourRep[self.currentContour].ClearAllNodes()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
            self.parent.render_window.Render()
            return
        if ch in ['r', 'R']:
            space = self.parent.space
            if len(space) == 2:
                space += [1]
            point_array = self.getAllPoint() / space
            if point_array.shape[0] == 0:
                return
            
            sigmaMin = 4
            n = 1000
            d = 1.0 / self.parent.parent.getData().getResolution()[-1]
            center = point_array[0, 0:2]
            image = self.parent.parent.getData().getData()[point_array[0, 2], :, :].transpose()
            
            th = util.getThreshold(image, center, d, space[0:2], sigmaMin)
            resultPoints, distance = util.getRayPoints(image, center, n, th)
            
            point_array = npy.insert(resultPoints, 2, point_array[0, 2], axis = 1) * space
            self.contourRep[self.currentContour].ClearAllNodes()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].AddNodeAtWorldPosition(point_array[i, :].tolist())
            self.parent.render_window.Render()
            return
        super(AutoUSCenterlinePlugin, self).KeyPressCallback(obj, event)
    def autoDetectContour(self, point_vital, cnt, be, en, space):
        if be > en:
            step = -1
        else:
            step = 1
        sigmaMin = 4
        n = 1000
        d = 1.0 / self.parent.parent.getData().getResolution()[-1]
        
        points = point_vital[cnt][npy.round(point_vital[cnt][:, 2]) == be]
        if points is None:
            return
        points = points[:, :-2]
        center, diameter, angle = util.ellipseFitting(points)
        
        for i in range(be, en + step, step):
            print cnt, ': slice ', i
            image = self.parent.parent.getData().getData()[i, :, :].transpose()
            #th = util.getThreshold(image, center, d, space[0:2], sigmaMin)
            th, gradient_img = util.getGradientThresholdAndImage(image, center, d, space[0:2])
            #resultPoints, distance = util.getRayPoints(image, center, n, th)
            resultPoints, distance = util.getRayPoints(gradient_img, center, n, th)
            h, w = image.shape
            prunedPoints = util.finePrune(resultPoints, distance, center, diameter, angle, h, w)
            new_center, new_diameter, new_angle = util.ransac(prunedPoints, util.EllipseLeastSquaresModel(),
                50, 200, 50, 800)
            #new_center, new_diameter, new_angle = util.ellipseFitting(prunedPoints)
            if new_angle != -1:
                rate = new_diameter[0] * new_diameter[1] / (diameter[0] * diameter[1])
                if rate <= 1.5 and rate >= 0.7:
                    
                #print diameter[0] - new_diameter[0], diameter[1] - new_diameter[1]
                    center, diameter, angle = new_center, new_diameter, new_angle
            temp_array = util.getPointsFromEllipse(center, diameter, angle, 20)
            #temp_array = npy.array([[center[0], center[1], i]], dtype = npy.float32)
            temp_array = npy.insert(temp_array, [temp_array.shape[1]], npy.ones((temp_array.shape[0], 1), int) * i, axis = 1)
            #self.parent.parent.getData().pointSet.setSlicePoint('Centerline', temp_array, 2, i, cnt)
            self.parent.parent.getData().pointSet.setSlicePoint('Contour', temp_array, 2, i, cnt)
        
    def getName(self):
        return "Auto US Centerline Detector"
        
