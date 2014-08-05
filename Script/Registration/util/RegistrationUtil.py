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
def rotation2angle(R):
    # ZXY
    xx = npy.arcsin(R[2, 1])
    A = npy.cos(xx)
    if npy.abs(A) > 0.00005:
        yy = npy.arctan2(R[2, 0] / A, R[2, 2] / A)
        zz = npy.arctan2(R[0, 1] / A, R[1, 1] / A)
    else:
        zz = 0
        yy = npy.arctan2(R[1, 0], R[0, 0])
    return [xx, yy, zz]
def angle2rotation(theta):
    # ZXY
    xx, yy, zz = theta
    cx = npy.cos(xx)
    sx = npy.sin(xx)
    cy = npy.cos(yy)
    sy = npy.sin(yy)
    cz = npy.cos(zz)
    sz = npy.sin(zz)
    
    Rx = ml.mat([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = ml.mat([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = ml.mat([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    
    R = Rz * Rx * Ry
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
    
def augmentCenterline(ori_points, multiple, times):
    if multiple <= 1:
        multiple = 1.0
    multiple = int(times * multiple + 0.5)
    trans_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
    ind = ori_points[:, 2].argsort()
    ori_points = ori_points[ind]
    for cnt in range(3):
        resampled_points = ori_points[npy.where(npy.round(ori_points[:, -1]) == cnt)]
        
        count = resampled_points.shape[0]
        points = vtk.vtkPoints()
        for i in range(count):
            points.InsertPoint(i, resampled_points[i, 0], resampled_points[i, 1], resampled_points[i, 2])

        para_spline = vtk.vtkParametricSpline()
        para_spline.SetPoints(points)
        para_spline.ClosedOff()
        
        numberOfOutputPoints = count * multiple
        
        for i in range(0, numberOfOutputPoints):
            t = i * 1.0 / numberOfOutputPoints
            pt = [0.0, 0.0, 0.0]
            para_spline.Evaluate([t, t, t], pt, [0] * 9)
            trans_points = npy.append(trans_points, [[pt[0], pt[1], pt[2], cnt]], axis = 0)
    return trans_points    

def resliceTheResultPoints(moving_points, moving_center, nn, moving_res, fixed_res, discard, R, T, C = npy.asmatrix([0, 0, 0]).T):
    resampled_points = [None, None, None]
    nearbif_points = [None, None, None]
    nearbif_center = [None, None]
    bif_slice = 0
    
    for cnt in range(3):
        temp_result = moving_points[npy.where(npy.round(moving_points[:, -1]) == cnt)].copy()
        if not temp_result.shape[0]:
            continue
        zmin = int(npy.min(temp_result[:, 2]) + 0.5)
        zmax = int(npy.max(temp_result[:, 2]) + 0.5)
        
        resampled_points[cnt] = npy.zeros([(zmax - zmin + 1) * nn, 4], dtype = npy.float32)
        resampled_index = 0
        
        for z in range(zmin, zmax + 1):
            data_result = temp_result[npy.where(npy.round(temp_result[:, 2]) == z)]
            if data_result is not None:
                if data_result.shape[0] == 0:
                    continue
                
                center_result = calCentroidFromContour(data_result[:, :2])[0]
                points_result = getPointsOntheSpline(data_result, center_result, 900)
                if cnt > 0 and z == zmin:
                    nearbif_points[cnt] = points_result
                    nearbif_center[cnt - 1] = center_result
                    bif_slice = z
                elif cnt == 0 and z == zmax - 1:
                    nearbif_points[cnt] = points_result
                    
                i = 0
                for k in range(- nn / 2 + 1, nn / 2 + 1):
                    angle = k * 360 / nn / 180.0 * npy.pi
                    
                    while i < 900 and points_result[i, 2] < angle:
                        i += 1
                    if i == 900 or (i > 0 and angle - points_result[i - 1, 2] < points_result[i, 2] - angle):
                        ind_result = i - 1
                    else:
                        ind_result = i
                    
                    resampled_points[cnt][resampled_index, :2] = points_result[ind_result, :2]
                    resampled_points[cnt][resampled_index, 2] = z
                    resampled_points[cnt][resampled_index, 3] = k + nn / 2 - 1
                    resampled_index += 1
    
    nearbif_angle = [npy.arctan2(nearbif_center[1][1] - nearbif_center[0][1], nearbif_center[1][0] - nearbif_center[0][0]), 
                     npy.arctan2(nearbif_center[0][1] - nearbif_center[1][1], nearbif_center[0][0] - nearbif_center[1][0])]
    point_near_bif = npy.zeros([2, 2], dtype = npy.float32)
    for cnt in range(2):
        ind = npy.argmin(npy.abs(nearbif_points[cnt + 1][:, 2] - nearbif_angle[cnt]))
        point_near_bif[cnt, :] = nearbif_points[cnt + 1][ind, :2]
    bif_points = npy.zeros([3, 3], dtype = npy.float32)
    bif_points[0, :2] = npy.mean(point_near_bif, axis = 0)
    bif_points[0, 2] = bif_slice
    nearbif_angle = [npy.arctan2(nearbif_center[1][0] - nearbif_center[0][0], nearbif_center[0][1] - nearbif_center[1][1]), 
                     npy.arctan2(nearbif_center[0][0] - nearbif_center[1][0], nearbif_center[1][1] - nearbif_center[0][1])]
    nearbif_points[0][:, 2] = npy.arctan2(nearbif_points[0][:, 1] - bif_points[0, 1], nearbif_points[0][:, 0] - bif_points[0, 0])
    for cnt in range(1, 3):
        ind = npy.argmin(npy.abs(nearbif_points[0][:, 2] - nearbif_angle[cnt - 1]))
        bif_points[cnt, :2] = nearbif_points[0][ind, :2]
    bif_points[1:, 2] = bif_slice - 1
    
    # Apply the transformation on the resampled points
    for cnt in range(3):
        resampled_points[cnt][:, :3] = applyTransformForPoints(resampled_points[cnt][:, :3], moving_res, fixed_res, R, T, C)
    bif_points = applyTransformForPoints(bif_points, moving_res, fixed_res, R, T, C)

    # Resample the points near the bifurcation
    points = vtk.vtkPoints()
    points.InsertPoint(0, bif_points[1, 0], bif_points[1, 1], bif_points[1, 2])
    points.InsertPoint(1, bif_points[0, 0], bif_points[0, 1], bif_points[0, 2])
    points.InsertPoint(2, bif_points[2, 0], bif_points[2, 1], bif_points[2, 2])

    para_spline = vtk.vtkParametricSpline()
    para_spline.SetPoints(points)
    para_spline.ClosedOff()
    
    numberOfOutputPoints = 6
    new_bif_points = npy.zeros([numberOfOutputPoints + 1, 4], dtype = npy.float32)
    
    for i in range(0, numberOfOutputPoints + 1):
        t = i * 1.0 / numberOfOutputPoints
        pt = [0.0, 0.0, 0.0]
        para_spline.Evaluate([t, t, t], pt, [0] * 9)
        new_bif_points[i, :3] = pt
    new_bif_points[:, 3] = 0
    
    # Reslice the result points
    trans_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
    bif_slice = int(npy.ceil(bif_points[0, 2]))
    
    for cnt in range(3):
        zmin = int(npy.ceil(npy.max(resampled_points[cnt][:nn, 2])))
        zmax = int(npy.min(resampled_points[cnt][-nn:, 2]))
        if not discard:
            if cnt == 0:
                zmax = bif_slice
            else:
                zmin = bif_slice
        
        for k in range(0, nn):
            data = resampled_points[cnt][npy.where(npy.round(resampled_points[cnt][:, -1]) == k)]
            if not discard:
                if cnt == 0:
                    dis1 = npy.hypot(data[-1, 0] - resampled_points[1][nn:nn * 2, 0], data[-1, 1] - resampled_points[1][nn:nn * 2, 1])
                    #dis1 = npy.hypot(data[-1, 0] - nearbif_points[1][:, 0], data[-1, 1] - nearbif_points[1][:, 1])
                    ind1 = npy.argmin(dis1)
                    dis2 = npy.hypot(data[-1, 0] - resampled_points[2][nn:nn * 2, 0], data[-1, 1] - resampled_points[2][nn:nn * 2, 1])
                    ind2 = npy.argmin(dis2)
                    if dis1[ind1] < dis2[ind2]:
                        data_add = resampled_points[1][npy.where((npy.round(resampled_points[1][:, -1]) == ind1) & (resampled_points[1][:, 2] <= zmax + 1))]
                    else:
                        data_add = resampled_points[2][npy.where((npy.round(resampled_points[2][:, -1]) == ind2) & (resampled_points[2][:, 2] <= zmax + 1))]
                    data = npy.append(data, data_add[1:, :], axis = 0)
                else:
                    dis1 = npy.hypot(data[0, 0] - resampled_points[0][-nn * 2:-nn, 0], data[0, 1] - resampled_points[0][-nn * 2:-nn, 1])
                    ind1 = npy.argmin(dis1)
                    dis2 = npy.sqrt(npy.sum((new_bif_points[:, :3] - data[0, :3]) ** 2, axis = 1))
                    ind2 = npy.argmin(dis2)
                    if dis1[ind1] < dis2[ind2]:
                        data_add = resampled_points[0][npy.where((npy.round(resampled_points[0][:, -1]) == ind1) & (resampled_points[0][:, 2] >= zmin - 1))]
                    else:
                        data_add = new_bif_points[ind2, :].reshape(1, -1)
                    data = npy.append(data_add[:-1, :], data, axis = 0)
                
            count = data.shape[0]
            if count == 0:
                continue
            points = vtk.vtkPoints()
            for i in range(count):
                points.InsertPoint(i, data[i, 0], data[i, 1], data[i, 2])
    
            para_spline = vtk.vtkParametricSpline()
            para_spline.SetPoints(points)
            para_spline.ClosedOff()
            
            znow = zmin
            old_pt = [0.0, 0.0, 0.0]
            numberOfOutputPoints = int((zmax - zmin + 3) * nn)
            
            for i in range(0, numberOfOutputPoints):
                t = i * 1.0 / numberOfOutputPoints
                pt = [0.0, 0.0, 0.0]
                para_spline.Evaluate([t, t, t], pt, [0] * 9)
                if pt[2] >= znow:
                    if pt[2] - znow < znow - old_pt[2]:
                        new_point = pt
                    else:
                        new_point = old_pt
                    trans_points = npy.append(trans_points, [[new_point[0], new_point[1], znow, cnt]], axis = 0)
                    znow += 1
                    if znow > zmax:
                        break
                old_pt = pt
    
    new_trans_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
    for cnt in range(3):
        temp_result = trans_points[npy.where(npy.round(trans_points[:, -1]) == cnt)]
        if not temp_result.shape[0]:
            continue
        zmin = int(npy.min(temp_result[:, 2]) + 0.5)
        zmax = int(npy.max(temp_result[:, 2]) + 0.5)
        for z in range(zmin, zmax + 1):
            data_result = temp_result[npy.where(npy.round(temp_result[:, 2]) == z)]
            if data_result is not None:
                if data_result.shape[0] == 0:
                    continue
                
                center_result = calCentroidFromContour(data_result[:, :2])[0]
                if data_result.shape[0] >= 4:
                    # Sort the pointSet for a convex contour
                    point = npy.delete(data_result, 2, axis = 1)
                    #core = point.mean(axis = 0)
                    core = center_result[:2]
                    point[:, :2] -= core
                    angle = npy.arctan2(point[:, 1], point[:, 0])
                    ind = angle.argsort()
                    data_result[:, :] = data_result[ind, :]
                for x in data_result:
                    if isDifferent(new_trans_points[-1, :], x):
                        new_trans_points = npy.append(new_trans_points, x.reshape(1, -1), axis = 0)
                    
                        
    result_center_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
    if moving_center is not None and moving_center.shape[0] > 1:
        result_center = moving_center[npy.where(moving_center[:, 0] >= 0)]
        
        result_center[:, :3] = applyTransformForPoints(result_center[:, :3], moving_res, fixed_res, R, T, C)
        ind = result_center[:, 2].argsort()
        result_center = result_center[ind]
        
        result_center_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        for cnt in range(3):
            resampled_points = result_center[npy.where(npy.round(result_center[:, -1]) == cnt)]
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
                    result_center_points = npy.append(result_center_points, [[new_point[0], new_point[1], znow, cnt]], axis = 0)
                    znow += 1
                    if znow > zmax:
                        break
                old_pt = pt
    return new_trans_points, result_center_points
    
def applyTransformForPoints(points, moving_res, fixed_res, R, T, C = npy.asmatrix([0, 0, 0]).T):
    points[:, :3] *= moving_res[:3]
    points[:, :3] -= C.T
    if T.shape[1] == 1:
        TT = ml.ones((points.shape[0], 1)) * T.T
    else:
        TT = T
    temp = ml.mat(points[:, :3]) * R + TT + ml.ones((points.shape[0], 1)) * C.T
    points[:, :3] = temp
    points[:, :3] /= fixed_res[:3]
    return points
def isDifferent(p1, p2):
    if p1[-1] != p2[-1]:
        return True
    if npy.round(p1[2]) == npy.round(p2[2]) and npy.hypot(p1[0] - p2[0], p1[1] - p2[1]) < 0.1:
        return False
        
    return True


