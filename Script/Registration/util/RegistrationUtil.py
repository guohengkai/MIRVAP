# -*- coding: utf-8 -*-
"""
Created on 2014-04-24

@author: Hengkai Guo
"""

import numpy as npy
import numpy.matlib as ml
import vtk
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCentroidFromContour

def quaternion2rotation(q):
    R = ml.zeros([3, 3], dtype = npy.float32)
    x, y, z, r = q
    x2, y2, z2, r2 = q * q
    
    R[0, 0] = r2 + x2 - y2 - z2
    R[1, 1] = r2 - x2 + y2 - z2
    R[2, 2] = r2 - x2 - y2 + z2
    
    R[1, 0] = 2 * (x * y + r * z)
    R[2, 0] = 2 * (z * x - r * y)
    R[2, 1] = 2 * (y * z + r * x)
    R[0, 1] = 2 * (x * y - r * z)
    R[0, 2] = 2 * (z * x + r * y)
    R[1, 2] = 2 * (y * z - r * x)
    
    ss = x2 + y2 + z2 + r2
    R = R / ss
    return R
def getPointsOntheSpline(data, center, numberOfOutputPoints):
    if data.shape[0] >= 4:
        # Sort the pointSet for a convex contour
        point = npy.delete(data, 2, axis = 1)
        #core = point.mean(axis = 0)
        core = center[:2]
        point[:, :2] -= core
        angle = npy.arctan2(point[:, 1], point[:, 0])
        ind = angle.argsort()
        data[:, :] = data[ind, :]
        
    count = data.shape[0]
    points = vtk.vtkPoints()
    for j in range(count):
        points.InsertPoint(j, data[j, 0], data[j, 1], 0)
    
    para_spline = vtk.vtkParametricSpline()
    para_spline.SetPoints(points)
    para_spline.ClosedOn()
    
    result = npy.empty([numberOfOutputPoints, 3], dtype = npy.float32)
    
    for k in range(0, numberOfOutputPoints):
        t = k * 1.0 / numberOfOutputPoints
        pt = [0.0, 0.0, 0.0]
        para_spline.Evaluate([t, t, t], pt, [0] * 9)
        result[k, :2] = pt[:2]
        
    result[:, 2] = npy.arctan2(result[:, 1] - center[1], result[:, 0] - center[0])
    ind = result[:, 2].argsort()
    return result[ind, :]

def augmentPointset(ori_points, multiple, opt_size, bif, nn = -1):
    if multiple <= 1:
        return ori_points
    if nn < 0:
        zmin = int(npy.min(ori_points[:, 2]) + 0.5)
        zmax = int(npy.max(ori_points[:, 2]) + 0.5)
        nn = int((opt_size - ori_points.shape[0]) / ((2 * zmax - zmin - bif)) / (multiple - 1) + 0.5) + 1
        #print nn
    
    new_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
    zmin = [0, 0, 0]
    zmax = [0, 0, 0]
    resampled_points = [None, None, None]
    for cnt in range(3):
        temp_result = ori_points[npy.where(npy.round(ori_points[:, -1]) == cnt)]
        if not temp_result.shape[0]:
            continue
        zmin[cnt] = int(npy.min(temp_result[:, 2]) + 0.5)
        zmax[cnt] = int(npy.max(temp_result[:, 2]) + 0.5)
        resampled_points[cnt] = npy.zeros([(zmax[cnt] - zmin[cnt] + 1) * nn, 4], dtype = npy.float32)
        resampled_index = 0
        
        for z in range(zmin[cnt], zmax[cnt] + 1):
            data_result = temp_result[npy.where(npy.round(temp_result[:, 2]) == z)]
            if data_result is not None:
                if data_result.shape[0] == 0:
                    continue
                
                #center_result = npy.mean(data_result[:, :2], axis = 0)
                center_result = calCentroidFromContour(data_result[:, :2])[0]
                points_result = getPointsOntheSpline(data_result, center_result, 900)
                
                i = 0
                for k in range(-nn / 2 + 1, nn / 2 + 1):
                    angle = k * 2 * npy.pi / nn 
                    
                    while i < 900 and points_result[i, 2] < angle:
                        i += 1
                    if i == 900 or (i > 0 and angle - points_result[i - 1, 2] < points_result[i, 2] - angle):
                        ind_result = i - 1
                    else:
                        ind_result = i
                    
                    resampled_points[cnt][resampled_index, :2] = points_result[ind_result, :2]
                    resampled_points[cnt][resampled_index, 2] = z
                    resampled_points[cnt][resampled_index, 3] = k + 4
                    resampled_index += 1
    trans_points = npy.array(ori_points)
    for cnt in range(3):
        for k in range(0, nn):
            data = resampled_points[cnt][npy.where(npy.round(resampled_points[cnt][:, -1]) == k)]
            count = data.shape[0]
            if count == 0:
                continue
            points = vtk.vtkPoints()
            for i in range(count):
                points.InsertPoint(i, data[i, 0], data[i, 1], data[i, 2])
    
            para_spline = vtk.vtkParametricSpline()
            para_spline.SetPoints(points)
            para_spline.ClosedOff()
            
            deltaz = 1.0 / multiple
            old_pt = [0.0, 0.0, 0.0]
            numberOfOutputPoints = int((zmax[cnt] - zmin[cnt] + 1) * 10)
            i = 0
            
            for z in range(zmin[cnt], zmax[cnt] + 1):
                znow = float(z)
                for dd in range(1, multiple):
                    znow += deltaz 
                    while i < numberOfOutputPoints:
                        t = i * 1.0 / numberOfOutputPoints
                        pt = [0.0, 0.0, 0.0]
                        para_spline.Evaluate([t, t, t], pt, [0] * 9)
                        if pt[2] >= znow:
                            if pt[2] - znow < znow - old_pt[2]:
                                new_point = pt
                            else:
                                new_point = old_pt
                            trans_points = npy.append(trans_points, [[new_point[0], new_point[1], znow, cnt]], axis = 0)
                            
                            old_pt = pt
                            break
                        i += 1
    return trans_points
