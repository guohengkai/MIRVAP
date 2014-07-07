# -*- coding: utf-8 -*-
"""
Created on 2014-04-08

@author: Hengkai Guo
"""

import DataBase as db
from LoadBase import LoadBase

import numpy as npy
import dicom
import SimpleITK as sitk


class LoadDicomDir(LoadBase):
    def __init__(self, gui):
        super(LoadDicomDir, self).__init__(gui)
    def getName(self):
        return 'Load from dicom directory'
    def getLoadParameters(self):
        title = 'Select DICOM Directory'
        dir = 'Test/Data'
        filter = 'All Files(*.*)'
        return title, dir, filter
    def run(self, *args, **kwargs):
        title, dir, filter = self.getLoadParameters()
        dir = self.gui.getDirName(title, dir, filter)
        if dir:
            return self.load(dir)
        else:
            return []
    def load(self, dir):
        try:
            data, names = db.loadDicomArrayFromDir(dir)
        except Exception:
            self.gui.showErrorMessage("Memory error", "Data exceeded memory limit! If this problem occurs again, please restart the application.")
            return []
        
        # Format: z * x * y
        if type(data) == tuple:
            data = npy.concatenate((data[0], data[1]), axis = 0)
        if data.shape[0] == 1:
            data = data.reshape(data.shape[1:])
            
        info = self.loadDicomInfo(names[0], len(data.shape))
        fileData = db.BasicData(data = data, info = info)
        
        return [fileData]
        
    def loadDicomInfo(self, dir, dimension):
        # Only available for special data (Need to modify for more universal usage)
        info = db.ImageInfo()
        data = dicom.read_file(dir)
        modality = data.Modality
        info.addData('modality', modality)
        if modality == 'MR' or modality == 'CT':
            ps = data.PixelSpacing
            if modality == 'MR':
                z = data.SpacingBetweenSlices
            else:
                z = data.SliceThickness
            if dimension == 3:
                resolution = [float(z), float(ps[0]), float(ps[1])]
            else:
                resolution = [float(ps[0]), float(ps[1])]   
            resolution = npy.array(resolution)
            info.addData('resolution', resolution)
            orientation = npy.array(map(float, data.ImageOrientationPatient))
            info.addData('orientation', orientation)
        elif modality == 'US':
            r = data[0x200d, 0x3303].value
            resolution = npy.array([float(r[2]), float(r[1]), float(r[0])])
            info.addData('resolution', resolution)
            orientation = npy.array(map(float, data[0x200d, 0x3d00].value[0][0x0020, 0x9116].value[0][0x200d, 0x3d16].value))
            info.addData('orientation', orientation)
            
        # To make the orientation of images compatible
        view, flip = db.getViewAndFlipFromOrientation(orientation, resolution.shape[0])
        info.addData('view', view)
        info.addData('flip', flip)

        return info
