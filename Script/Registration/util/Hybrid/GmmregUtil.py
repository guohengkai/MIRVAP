# -*- coding: utf-8 -*-
"""
Created on 2014-08-03

@author: Hengkai Guo
"""

import numpy as npy
import numpy.matlib as ml
import vtk

def ComputeTPSKernel(model, ctrl_pts):
    m = model.shape[0]
    n = ctrl_pts.shape[0]
    M = ml.mat(model)
    C = ml.mat(ctrl_pts)
    result = ml.zeros([m, n], dtype = npy.float32)
    
    for i in range(m):
        for j in range(n):
            v = M[i, :] - C[j, :]
            r = npy.linalg.norm(v)
            result[i, j] = -r
    
    return result

def getControlPoints(points, step):
    ctrl_pts = npy.array([[-1, -1, -1.0]])
    
    ind = points[:, 2].argsort()
    points_sort = points[ind]
    
    for cnt in range(3):
        resampled_points = points_sort[npy.where(npy.round(points_sort[:, -1]) == cnt)]
        zmin = int(npy.ceil(resampled_points[0, 2]))
        zmax = int(resampled_points[-1, 2])
        
        count = resampled_points.shape[0]
        points = vtk.vtkPoints()
        for i in range(count):
            points.InsertPoint(i, resampled_points[i, 0], resampled_points[i, 1], resampled_points[i, 2])

        para_spline = vtk.vtkParametricSpline()
        para_spline.SetPoints(points)
        para_spline.ClosedOff()
        
        znow = zmin
        old_pt = [0.0, 0.0, 0.0]
        numberOfOutputPoints = int((zmax - zmin + 1) * 10)
        
        for i in range(0, numberOfOutputPoints):
            t = i * 1.0 / numberOfOutputPoints
            pt = [0.0, 0.0, 0.0]
            para_spline.Evaluate([t, t, t], pt, [0] * 9)
            if pt[2] >= znow:
                if pt[2] - znow < znow - old_pt[2]:
                    new_point = pt
                else:
                    new_point = old_pt
                ctrl_pts = npy.append(ctrl_pts, [[new_point[0], new_point[1], znow]], axis = 0)
                znow += step
                if znow > zmax:
                    break
            old_pt = pt
    
    ctrl_pts = ctrl_pts[1:, :]
    return ctrl_pts
