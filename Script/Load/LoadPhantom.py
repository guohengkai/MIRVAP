# -*- coding: utf-8 -*-
"""
Created on 2014-03-11

@author: Hengkai Guo
"""

from MIRVAP.Script.LoadBase import LoadBase
import MIRVAP.Core.DataBase as db

import numpy as npy

# Need to be more flexible
class LoadPhantom(LoadBase):
    def __init__(self, gui):
        super(LoadPhantom, self).__init__(gui)
    def getName(self):
        return 'Generate Phantom Data'
    def run(self, *args, **kwargs):
        num, ok = self.gui.getInputPara(self.gui.win, 'centerX')
        if ok and num:
            centerx = float(num)
            num, ok = self.gui.getInputPara(self.gui.win, 'centerY')
            if ok and num:
                centery = float(num)
                
                info = self.getInfo(res = [1.0, 1.0, 1.0], ori = 0)
                image = self.getImage(size = [150, 200, 300], center = [centerx, centery, 0])
                point = self.getPointSet(size = [150, 200, 300], ori = 0, center = [centerx, centery, 0])
        
                phantomData = db.BasicData(data = image, info = info, pointSet = point)
                return phantomData
        
        
    def getInfo(self, res = [1.0, 1.0, 1.0], ori = 0):
        info = db.ImageInfo()
        info.addData('modality', 'MR') 
        resolution = npy.array(res)
        info.addData('resolution', resolution)
        if ori == 0: # z
            orientation = npy.array([1, 0, 0, 0, 1, 0])
        elif ori == 1: # y
            orientation = npy.array([1, 0, 0, 0, 0, -1])
        elif ori == 2: # x
            orientation = npy.array([0, 1, 0, 0, 0, -1])
        info.addData('orientation', orientation)
        
        view, flip = db.getViewAndFlipFromOrientation(orientation, resolution.shape[0])
        info.addData('view', view)
        info.addData('flip', flip)
        
        return info
        
    def getImage(self, size = [100, 100, 100], radius = 30, center = [49.5, 49.5, 49.5], black = 0, gray = 100):
        
        image = npy.ones(size[::-1], npy.float32) * black
        
        for i in range(size[0]):
            for j in range(size[1]):
                if ((i - center[0]) ** 2 + (j - center[1]) ** 2 <= radius ** 2):
                    image[:, j, i] = gray
        
        return image
    def getPointSet(self, size = [100, 100, 100], radius = 30, center = [49.5, 49.5, 49.5], ori = 0, count = 20):
        point = dict()
        pos = 2 - ori
        c = [0, 1, 2]
        del c[pos]
        
        centerline = npy.ones((size[pos], 4), npy.float32)
        centerline[:, -1] = 0
        centerline[:, 0 : 3] = center
        centerline[:, pos] = range(size[pos])
        point['Centerline'] = centerline
        
        contour = npy.ones((size[pos] * count, 4), npy.float32)
        contour[:, -1] = 0;
        circleX = npy.cos(npy.arange(count) * npy.pi * 2 / count) * radius + center[c[0]]
        circleY = npy.sin(npy.arange(count) * npy.pi * 2 / count) * radius + center[c[1]]
        contour[:, c[0]] = circleX.tolist() * size[pos]
        contour[:, c[1]] = circleY.tolist() * size[pos]
        contour[:, pos] = npy.arange(size[pos]).repeat(count)
        point['Contour'] = contour
        
        return point
        
