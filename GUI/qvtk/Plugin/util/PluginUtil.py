# -*- coding: utf-8 -*-
"""
Created on 2014-04-27

@author: Hengkai Guo
"""

import numpy as npy

def calCenterlineFromContour(data):
    # Get the input information (begin, end, bifurcation)
    point_data_result = npy.array(data['Contour'])
    center_data = npy.array([[-1, -1, -1, -1]])
    if point_data_result is None or not point_data_result.shape[0]:
        return None
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
                current_center = calCentroidFromContour(data[:, :2])
                current_center = npy.append(current_center, [[i, cnt]], axis = 1)
                center_data = npy.append(center_data, current_center, axis = 0)
    return center_data            

def calCentroidFromContour(data):
    temp_area = npy.zeros([data.shape[0]])
    data = npy.append(data, [[data[0, 0], data[0, 1]]], axis = 0)
    for j in range(temp_area.shape[0]):
        temp_area[j] = data[j, 0] * data[j + 1, 1] - data[j + 1, 0] * data[j, 1]
    
    current_center = npy.array([[0.0, 0.0]])
    for j in range(temp_area.shape[0]):
        for k in range(2):
            current_center[0, k] += (data[j, k] + data[j + 1, k]) * temp_area[j]
    current_center[0, :2] /= 3 * npy.sum(temp_area)
    
    return current_center
