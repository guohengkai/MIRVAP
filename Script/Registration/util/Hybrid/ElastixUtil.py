# -*- coding: utf-8 -*-
"""
Created on 2014-08-03

@author: Hengkai Guo
"""

import numpy as npy
import numpy.matlib as ml
import vtk
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_function import ac_mask
import MIRVAP.Script.Registration.util.RegistrationUtil as util
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import sortContourPoints
import MIRVAP.Core.DataBase as db

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
                
    return npy.cast['float32'](data)
    
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
                
                ind = sortContourPoints(data_point)
                data_point = data_point[ind]
                
                data_point = data_point[:, :2].transpose()
                data[z, :, :] = data[z, :, :] | ac_mask(data_point, image_size).transpose()
                        
    return npy.cast['float32'](data)

def getBifurcationOfCenterline(pointset):
    z = pointset[:, 2]
    ind0 = npy.argmax(z[npy.round(pointset[:, -1]) == 0])
    ind1 = npy.argmin(z[npy.round(pointset[:, -1]) == 1])
    ind2 = npy.argmin(z[npy.round(pointset[:, -1]) == 2])

    point = npy.mean(pointset[[ind0, ind1, ind2], :3], axis = 0)
    return point
    
def getKeyPoints(pointset, res, radius = [5.0, 8.0, 10.0]):
    l = len(radius)
    result = npy.zeros([1 + 3 * l, 3], dtype = npy.float32)
    result[0, :] = getBifurcationOfCenterline(pointset) * res

    point_tmp = pointset.copy()
    point_tmp[:, :3] *= res

    # Calculate the distance to bifurcation for each points
    d = npy.sqrt(((point_tmp[:, 0] - result[0, 0]) * res[0]) ** 2 + \
                 ((point_tmp[:, 1] - result[0, 1]) * res[1]) ** 2 + \
                 ((point_tmp[:, 2] - result[0, 2]) * res[2]) ** 2)

    # Get the points for each radius
    i = 0
    for r in radius:
        # Get the points for vessel
        for cnt in range(3):
            ind = npy.where(npy.round(point_tmp[:, -1]) == cnt)
            pr = point_tmp[ind]
            dr = npy.abs(d[ind] - r)
            min_ind = npy.argmin(dr)
            result[i, :] = pr[min_ind, :3]
            i += 1
    
    return result # In real resolution
    
# Input 9 points for each image, output the rigid transform matrix (4 * 4)
def getRigidTransform(fix, mov): # In real resolution
    LandmarkTransform = vtk.vtkLandmarkTransform()
    LandmarkTransform.SetModeToRigidBody()
    
    n = fix.shape[0]
    fix_point = vtk.vtkPoints()
    fix_point.SetNumberOfPoints(n)
    mov_point = vtk.vtkPoints()
    mov_point.SetNumberOfPoints(n)

    for i in range(n):
        fix_point.SetPoint(i, fix[i, 0], fix[i, 1], fix[i, 2])
        mov_point.SetPoint(i, mov[i, 0], mov[i, 1], mov[i, 2])

    LandmarkTransform.SetSourceLandmarks(mov_point)
    LandmarkTransform.SetTargetLandmarks(fix_point)
    LandmarkTransform.Update()

    matrix = LandmarkTransform.GetMatrix()
    T = ml.zeros([4, 4], dtype = npy.float32)
    for i in range(4):
        for j in range(4):
            T[i, j] = matrix.GetElement(j, i)

    p1 = mov[0, :].tolist()
    p2 = [0.0, 0, 0]
    LandmarkTransform.InternalTransformPoint(p1, p2)
    
    return T, npy.array(p2)
    
def applyRigidTransformOnPoints(points, res, T): # Y = XT
    X = ml.ones([points.shape[0], 4], dtype = npy.float32)
    tmp = points.copy()
    tmp[:, :3] *= res
    X[:, :3] = tmp[:, :3]
    Y = X * T
    result_points = npy.array(points.copy())
    result_points[:, :3] = Y[:, :3]
    result_points[:, :3] /= res
    return result_points
    
def getMatrixFromGmmPara(para):
    R = ml.mat(para[:9]).reshape(3, 3)
    T0 = ml.mat(para[9:12]).T
    if len(para) > 12:
        C = ml.mat(para[12:])
    else:
        C = ml.zeros([1, 3], dtype = npy.float32)
    T0 = R.I * T0
    T0 = -T0.T

    T = ml.zeros([4, 4], dtype = npy.float32)
    T[-1, -1] = 1
    T[:3, :3] = R
    T[-1, :3] = T0 + C - C * R
    
    return T
    
def getElastixParaFromMatrix(T):
    para = npy.zeros(9, dtype = npy.float32)

    para[:3] = util.rotation2angle(T[:3, :3])
    para[3:6] = T[-1, :3]
    
    return para # The center can be always set to zeros

def cropCenterline(fix, mov, fix_res, mov_res, fix_bif, mov_bif):
    fix_max = npy.max(fix[:, 2])
    fix_min = npy.min(fix[:, 2])
    mov_max = npy.max(mov[:, 2])
    mov_min = npy.min(mov[:, 2])

    up_dis = min((fix_max - fix_bif) * fix_res[2], (mov_max - mov_bif) * mov_res[2])
    down_dis = min((fix_bif - fix_min) * fix_res[2], (mov_bif - mov_min) * mov_res[2])

    fix_index = npy.where((fix[:, 2] <= fix_bif + up_dis / fix_res[2]) & (fix[:, 2] >= fix_bif - down_dis / fix_res[2]))
    mov_index = npy.where((mov[:, 2] <= mov_bif + up_dis / mov_res[2]) & (mov[:, 2] >= mov_bif - down_dis / mov_res[2]))
    return fix_index, mov_index
