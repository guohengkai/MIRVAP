# -*- coding: utf-8 -*-
"""
Created on 2014-08-03

@author: Hengkai Guo
"""

import numpy as npy
import numpy.matlib as ml
import vtk
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_function import ac_mask

def getMaskFromCenterline(image, pointset, spacing, radius = 10):
    data = npy.zeros(image.shape, dtype = npy.uint8)
    image_size = image[0, :, :].transpose().shape
    n_pt = 20
    
    for cnt in range(3):
        temp_point = pointset[npy.where(npy.round(pointset[:, -1]) == cnt)]
        if not temp_point.shape[0]:
            continue
        zmin = int(npy.min(temp_point[:, 2]) + 0.5)
        zmax = int(npy.max(temp_point[:, 2]) + 0.5)
        
        for z in range(zmin, zmax + 1):
            center_point = temp_point[npy.where(npy.round(temp_point[:, 2]) == z)]
            if center_point is not None:
                if center_point.shape[0] == 0:
                    continue
                
                data_point = npy.zeros([n_pt, 2], dtype = npy.float32)
                for i in range(0, n_pt):
                    data_point[i, 0] = center_point[0, 0] + radius * npy.cos(2 * npy.pi * i / n_pt) / spacing[0]
                    data_point[i, 1] = center_point[0, 1] + radius * npy.sin(2 * npy.pi * i / n_pt) / spacing[1]
                
                data[z, :, :] = data[z, :, :] | ac_mask(data_point.transpose(), image_size).transpose()
                
    return data
    
def getBinaryImageFromSegmentation(image, pointset):
    data = npy.zeros(image.shape, dtype = npy.uint8)
    image_size = image[0, :, :].transpose().shape
    
    for cnt in range(3):
        temp_point = pointset[npy.where(npy.round(pointset[:, -1]) == cnt)]
        if not temp_point.shape[0]:
            continue
        zmin = int(npy.min(temp_point[:, 2]) + 0.5)
        zmax = int(npy.max(temp_point[:, 2]) + 0.5)
        
        for z in range(zmin, zmax + 1):
            data_point = temp_point[npy.where(npy.round(temp_point[:, 2]) == z)]
            if data_point is not None:
                if data_point.shape[0] == 0:
                    continue
                data_point = data_point[:, :2].transpose()
                data[z, :, :] = data[z, :, :] | ac_mask(data_point, image_size).transpose()
                        
    return data
