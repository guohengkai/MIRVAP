# -*- coding: utf-8 -*-
"""
Created on 2014-02-01

@author: Hengkai Guo
"""

class DataBase(object):
    def getData(self):
        raise NotImplementedError('Method "getArrayData" Not Impletemented!')

import numpy as npy
import SimpleITK as sitk
import itk
import scipy.io as sio
import copy as cp

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
    def getITKImage(self, imageType = None):
        if imageType == None:
            imageType = self.getITKImageType()
        image = itk.PyBuffer[imageType].GetImageFromArray(self.getData())
        image.SetSpacing(self.getResolution().tolist())
        return image
    def getSimpleITKImage(self):
        image = sitk.GetImageFromArray(self.getData())
        image.SetSpacing(self.getResolution().tolist())
        return image
    def getDimension(self):
        return self.data.ndim
    def getITKImageType(self):
        return itk.Image[itk.F, len(self.data.shape)]
        
    def setDataFromArray(self, data):
        self.data = data
    def setDataFromITKImage(self, data, imageType):
        self.data = itk.PyBuffer[imageType].GetArrayFromImage(data)
    def setDataFromSimpleITKImage(self, data):
        self.data = sitk.GetArrayFromImage(data)
    def setData(self, data, imageType = None):
        if isinstance(data, npy.ndarray):
            self.setDataFromArray(data)
        elif isinstance(data, sitk.Image):
            self.setDataFromSimpleITKImage(data)
        elif imageType is not None:
            self.setDataFromITKImage(data, imageType)
            
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
        
class ResultData(BasicData):
    def __init__(self, data = None, info = None, pointSet = None):
        super(ResultData, self).__init__(data, info, pointSet)
    def getFixedIndex(self):
        return self.info.getData('fix')
    def getMovingIndex(self):
        return self.info.getData('move')
    def addDetail(self, key, value):
        self.info.addData(key, value)

def getBifurcation(points):
    temp = points[:, 2:]
    temp2 = temp[npy.where(npy.round(temp[:, 1]) == 0), 0]
    if temp2.size == 0:
        return -1
    min1 = npy.round(npy.min(temp2))
    max1 = npy.round(npy.max(temp2))
    temp3 = temp[npy.where(npy.round(temp[:, 1]) == 1), 0]
    if temp3.size == 0:
        return -1
    min2 = npy.round(npy.min(temp3))
    max2 = npy.round(npy.max(temp3))
    if min1 == max2:
        return min1
    if min2 == max1:
        return min2
    return -1
def loadDicomArrayFromDir(dir):
    imageReader = sitk.ImageSeriesReader()
    names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dir, True)
    print names
    imageReader.SetFileNames(names)
    image = imageReader.Execute()
    del imageReader
    if len(names) < 80:
        array = sitk.GetArrayFromImage(image)
    else:
        imSize = image.GetSize()[-1]
        cropSize = imSize / 2
        cropFilter = sitk.CropImageFilter()
        cropFilter.SetLowerBoundaryCropSize([0, 0, 0])
        cropFilter.SetUpperBoundaryCropSize([0, 0, cropSize])
        array1 = sitk.GetArrayFromImage(cropFilter.Execute(image))
        cropFilter.SetLowerBoundaryCropSize([0, 0, imSize - cropSize])
        cropFilter.SetUpperBoundaryCropSize([0, 0, 0])
        array = sitk.GetArrayFromImage(cropFilter.Execute(image))
        
        array = (array1, array)
        del array1, image
        array = npy.concatenate((array[0], array[1]), axis = 0)
    return array, names
def loadDicomArray(dir):
    # When the amount of files exceeds 80+, the GetArrayFromImage function may crash, because of the memory limit of array in numpy
    if len(dir) == 1:
        imageReader = sitk.ImageFileReader()
        imageReader.SetFileName(dir[0])
    else:
        imageReader = sitk.ImageSeriesReader()
        imageReader.SetFileNames(dir)
    
    image = imageReader.Execute()
    del imageReader
    if len(dir) < 80:
        array = sitk.GetArrayFromImage(image)
    else:
        imSize = image.GetSize()[-1]
        cropSize = imSize / 2
        cropFilter = sitk.CropImageFilter()
        cropFilter.SetLowerBoundaryCropSize([0, 0, 0])
        cropFilter.SetUpperBoundaryCropSize([0, 0, cropSize])
        array1 = sitk.GetArrayFromImage(cropFilter.Execute(image))
        cropFilter.SetLowerBoundaryCropSize([0, 0, imSize - cropSize])
        cropFilter.SetUpperBoundaryCropSize([0, 0, 0])
        array = sitk.GetArrayFromImage(cropFilter.Execute(image))
        
        array = (array1, array)
        #For crop 68
        #array = (array, array1)
        del array1, image
        array = npy.concatenate((array[0], array[1]), axis = 0)
    return array

def loadMatData(dir, datamodel):
    data = sio.loadmat(dir)
    
    image = data['image']
    point = data.get('point')
    if point is not None:
        name = point.dtype.names
        pointSet = dict(zip(name, [point[key][0][0] for key in name]))
    else:
        pointSet = {}
    
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
    
    fixedImage = data.get('fixedImage')
    if fixedImage is not None:
        transform = data.get('transform', [])
        info.addData('transform', transform)
        movingImage = data.get('movingImage')
        
        resolution = header['resolution'][0][1][0]
        orientation = header['orientation'][0][1][0]
        clip = header['clip'][0][1][0]
        modality = str(header['modality'][0][1][0])
        name = str(header['name'][0][1][0])
        info1 = ImageInfo({'modality': modality, 'resolution': resolution, 
            'orientation': orientation, 'name': name, 'clip': clip})
        view, flip = getViewAndFlipFromOrientation(orientation, resolution.shape[0])
        info1.addData('view', view)
        info1.addData('flip', flip)
        
        resolution = header['resolution'][0][2][0]
        orientation = header['orientation'][0][2][0]
        clip = header['clip'][0][2][0]
        modality = str(header['modality'][0][2][0])
        name = str(header['name'][0][2][0])
        info2 = ImageInfo({'modality': modality, 'resolution': resolution, 
            'orientation': orientation, 'name': name, 'clip': clip})
        view, flip = getViewAndFlipFromOrientation(orientation, resolution.shape[0])
        info2.addData('view', view)
        info2.addData('flip', flip)
        
        point = data.get('fixedPoint')
        if point is not None:
            name = point.dtype.names
            pointSet1 = dict(zip(name, [point[key][0][0] for key in name]))
        else:
            pointSet1 = {}
            
        point = data.get('movingPoint')
        if point is not None:
            name = point.dtype.names
            pointSet2 = dict(zip(name, [point[key][0][0] for key in name]))
        else:
            pointSet2 = {}
            
        info.addData('fix', datamodel.append(BasicData(fixedImage, info1, pointSet1)))
        info.addData('move', datamodel.append(BasicData(movingImage, info2, pointSet2)))
    return image, info, pointSet

def saveMatData(dir, datamodel, index):
    data = datamodel[index]
    image = data.data
    point = data.getPointSet()
    
    resolution = data.info.getResolution()
    orientation = data.info.getData('orientation')
    clip = data.info.getData('clip')
    if clip is None:
        clip = npy.array([-1, -1, -1, -1, -1, -1])
    modality = npy.array([data.getModality()])
    name = npy.array([data.getName()])
    headerType = [('resolution', 'O'), ('orientation', 'O'), ('modality', 'O'), ('name', 'O'), ('clip', 'O')]
    header = npy.array([(resolution, orientation, modality, name, clip)], dtype = headerType)
    dict = {'image': image}
    if type(data) is ResultData:
        fixedIndex = data.getFixedIndex()
        fixedData = datamodel[fixedIndex]
        movingIndex = data.getMovingIndex()
        movingData = datamodel[movingIndex]
        clip1 = fixedData.info.getData('clip')
        if clip1 is None:
            clip1 = npy.array([-1, -1, -1, -1, -1, -1])
        clip2 = movingData.info.getData('clip')
        if clip2 is None:
            clip2 = npy.array([-1, -1, -1, -1, -1, -1])
        header = npy.append(header, npy.array([(fixedData.info.getResolution(), fixedData.info.getData('orientation'), 
                                                npy.array([fixedData.getModality()]), npy.array([fixedData.getName()]), clip1), 
                                               (movingData.info.getResolution(), movingData.info.getData('orientation'), 
                                                npy.array([movingData.getModality()]), npy.array([movingData.getName()]), clip2)], dtype = headerType))
        dict['fixedImage'] = datamodel[data.getFixedIndex()].data
        dict['movingImage'] = datamodel[data.getMovingIndex()].data
        dict['transform'] = data.info.getData('transform')
        
        temp = fixedData.getPointSet()
        if temp:
            pointSet = npy.array([tuple(temp.values())], dtype = [(key, 'O') for key in temp.keys()])
            dict['fixedPoint'] = pointSet
        temp = movingData.getPointSet()
        if temp:
            pointSet = npy.array([tuple(temp.values())], dtype = [(key, 'O') for key in temp.keys()])
            dict['movingPoint'] = pointSet
            
    dict['header'] = header
    if point:
        pointSet = npy.array([tuple(point.values())], dtype = [(key, 'O') for key in point.keys()])
        dict['point'] = pointSet
    
    sio.savemat(dir, dict)

def getViewAndFlipFromOrientation(orientation, dimension):
    '''
        Orientation: the direction cosines of the first row and the first
    column with respect to the patient. The direction of the axes are defined
    by the patients orientation to ensure LPS(Left, Posterior, Superior) system.
    ----------------------------------------------------------------------------
        1 0 0 0 1 0
        x: Sagittal slice * row
        y: Coronal  slice * col
        z: Axial    row * col
    ----------------------------------------------------------------------------
        1 0 0 0 0 -1
        x: Sagittal row * slice
        y: Coronal  row * col
        z: Axial    slice * col
    ----------------------------------------------------------------------------
        0 1 0 0 0 -1
        x: Sagittal row * slice
        y: Coronal  row * col
        z: Axial    slice * col
    ----------------------------------------------------------------------------
    '''
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
    
if __name__ == "__main__":
    basic = BasicData()
