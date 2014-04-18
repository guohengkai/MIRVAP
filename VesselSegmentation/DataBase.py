# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""

class DataBase(object):
    def getData(self):
        raise NotImplementedError('Method "getArrayData" Not Impletemented!')

import numpy as npy
import scipy.io as sio
import copy as cp
import os

class ImageInfo(DataBase):
    def __init__(self, data = None):
        if not data:
            data = {} # Default value of dictionary will point to the same address
        self.data = cp.deepcopy(data)
        
    def getData(self, key = None):
        if key is not None:
            return self.data.get(key)
        else:
            return self.data
    def getResolution(self):
        return self.getData('resolution')
    def getModality(self):
        return self.getData('modality')
    def getView(self):
        return self.getData('view')
    def getFlip(self):
        return self.getData('flip')
    def getName(self):
        return self.getData('name')
    def setName(self, name):
        self.data['name'] = name
        
    def setData(self, data):
        self.data = data
    def addData(self, key, value):
        self.data[key] = value
        
class ImageData(DataBase):
    def __init__(self, data = None, info = None):
        if data != None:
            data = data.astype(dtype = npy.float32)
        self.data = data
        self.info = info
        
    def getData(self):
        temp = self.getFlip()
        if len(temp) == 3:
            return self.data[::temp[0], ::temp[1], ::temp[2]].transpose(self.getView())
        else:
            return self.data[::temp[0], ::temp[1]].transpose(self.getView())
    def getDimension(self):
        return self.data.ndim
    def setDataFromArray(self, data):
        self.data = data
    def setData(self, data, imageType = None):
        if isinstance(data, npy.ndarray):
            self.setDataFromArray(data)
            
    def getInfo(self):
        return self.info
    def setInfo(self, info):
        self.info = info
    # Resolution: x(col), y(row), z(slice)
    def getResolution(self):
        if self.getDimension() == 3:
            return self.info.getResolution()[self.getView()[::-1]]
        else:
            return self.info.getResolution()
    def getModality(self):
        return self.info.getModality()
    def getView(self):
        return self.info.getView()
    def getFlip(self):
        return self.info.getFlip()
    def getName(self):
        if self.info:
            return self.info.getName()
    def setName(self, name):
        self.info.setName(name)

class PointSetData(DataBase):
    def __init__(self, data = None):
        if data is None:
            data = {}
        self.data = cp.deepcopy(data)
    def getData(self, key):
        if key not in self.data:
            self.data[key] = npy.array([[-1, -1, -1, -1]])
        return self.data[key]
    def getSlicePoint(self, key, axis, pos):
        data = self.getData(key)
        data = data[npy.where(npy.round(data[:, axis]) == npy.round(pos))]
        result = [npy.array([]), npy.array([]), npy.array([])]
        for cnt in range(3):
            result[cnt] = data[npy.where(npy.round(data[:, -1]) == cnt)]
            if result[cnt] is not None:
                result[cnt] = result[cnt][:, :-1]
        return result
    def setSlicePoint(self, key, data, axis, pos, cnt):
        data = npy.insert(data, [data.shape[1]], npy.ones((data.shape[0], 1), int) * cnt, axis = 1)
        self.getData(key)
        self.data[key] = npy.delete(self.data[key], npy.where((npy.abs(self.data[key][:, axis] - pos) < 0.0001) & (npy.round(self.data[key][:, -1]) == cnt)), axis = 0)
        self.data[key] = npy.append(self.data[key], data, axis = 0)

class BasicData(ImageData):
    def __init__(self, data = None, info = None, pointSet = None):
        super(BasicData, self).__init__(data, info)
        if pointSet is None:
            pointSet = {}
        self.pointSet = PointSetData(pointSet)
    def getPointSet(self, key = None):
        if key:
            return self.pointSet.getData(key)
        else:
            return self.pointSet.data
        
def loadMatData(dir):
    data = sio.loadmat(dir)
    
    image = data['image']
    
    header = data['header']
    resolution = header['resolution'][0][0][0]
    orientation = header['orientation'][0][0][0]
    clip = header['clip'][0][0][0]
    modality = str(header['modality'][0][0][0])
    name = str(header['name'][0][0][0])
    info = ImageInfo({'modality': modality, 'resolution': resolution, 
        'orientation': orientation, 'name': name, 'clip': clip})
    
    view, flip = getViewAndFlipFromOrientation(orientation, resolution.shape[0])
    info.addData('view', view)
    info.addData('flip', flip)
    
    return image, info
def loadMatPoint(dir):
    pointSet = {}
    if not os.path.exists(dir):
        return pointSet
    data = sio.loadmat(dir)
    
    point = data.get('point')
    if point is not None:
        name = point.dtype.names
        pointSet = dict(zip(name, [point[key][0][0] for key in name]))
    return pointSet

def saveMatPoint(dir, data, name):
    image = data.data
    point = data.getPointSet()
    
    pointSet = npy.array([tuple(point.values())], dtype = [(key, 'O') for key in point.keys()])
    dict = {'point': pointSet, 'name': name}
    
    sio.savemat(dir, dict)

def getViewAndFlipFromOrientation(orientation, dimension):
    ori = npy.round(orientation)
    col = npy.where(ori[0:3])[0][0]
    row = npy.where(ori[3:6])[0][0]
    
    if dimension == 3:
        view = npy.array([row - 1, 2 - row + col * 2, 2 - col * 2])
        flip = [1, ori[3 + row], ori[col]]
    else:
        view = npy.array([0, 1])
        flip = [1, 1]
        
    return (view, flip)
    
