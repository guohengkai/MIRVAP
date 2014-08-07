# -*- coding: utf-8 -*-
"""
Created on 2014-04-27

@author: Hengkai Guo
"""

import numpy as npy
import cv2, cv

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
                
                ind = sortContourPoints(data)
                data = data[ind]
                
                current_center = calCentroidFromContour(data[:, :2])
                current_center = npy.append(current_center, [[i, cnt]], axis = 1)
                center_data = npy.append(center_data, current_center, axis = 0)
    return center_data            

def calCentroidFromContour(data, area = False):
    temp_area = npy.zeros([data.shape[0]])
    data = npy.append(data, [[data[0, 0], data[0, 1]]], axis = 0)
    for j in range(temp_area.shape[0]):
        temp_area[j] = data[j, 0] * data[j + 1, 1] - data[j + 1, 0] * data[j, 1]
    
    current_center = npy.array([[0.0, 0.0]])
    for j in range(temp_area.shape[0]):
        for k in range(2):
            current_center[0, k] += (data[j, k] + data[j + 1, k]) * temp_area[j]
    current_center[0, :2] /= 3 * npy.sum(temp_area)
    
    if not area:
        return current_center
    else:
        return current_center, npy.abs(npy.sum(temp_area) / 2)

# Need to be tested
def calIntensityCentroidFromContour(image, pointset):
    mask = ac_mask(pointset[:, :2].transpose(), image.transpose().shape).transpose()
    result = image * mask
    cnt = npy.sum(mask)
    m00 = npy.sum(result) / cnt
    xx, yy = npy.mgrid[:image.shape[0], :image.shape[1]]
    m10 = npy.sum(xx * result) / cnt
    m01 = npy.sum(yy * result) / cnt
    
    center = npy.array([m10 / m00, m01 / m00])
    return center

# Most distant point in the contour(max(min(d(x, edge)))), need to be tested
def calCenterFromContour(image_size_trans, pointset):
    mask = ac_mask(pointset[:, :2].transpose(), image_size_trans).transpose()
    dist = cv2.distanceTransform(mask, cv.CV_DIST_L2, 3)
    value = npy.max(dist)

    indx, indy = npy.where(dist == npy.max(dist))
    indx = npy.cast['float32'](indx)
    indy = npy.cast['float32'](indy)

    center = npy.array([npy.mean(indx), npy.mean(indy)])
    return center

def sortConvexContourPoints(point_array): # Input: 2D pointset array
    point = point_array.copy()
    core = point.mean(axis = 0)
    point -= core
    angle = npy.arctan2(point[:, 1], point[:, 0])
    ind = angle.argsort()
    return ind

def sortContourPoints(point_array): # Input: 3D pointset array
    n = point_array.shape[0]
    if n < 4:
        return npy.arange(n, dtype = npy.uint8)
    elif n < 12: # Sort the pointSet for a convex contour
        return sortConvexContourPoints(npy.delete(point_array[:, :3], 2, axis = 1))
    else:
        point = point_array[:, :3].copy()
        
        for i in range(n):
            point[i, 2] = i # The serial number of points
        label = npy.zeros(n, dtype = npy.uint8)
        
        tmp_ind = npy.zeros(n, dtype = npy.uint8)
        tmp_diff = npy.zeros([n, 2], dtype = npy.float32)
        dis = 99999999
        flag = False
        for i in range(n - 1):
            for j in range(i + 1, n):
                # Select two points to seperate the pointset
                point_x = point[i, :]
                point_y = point[j, :]
                
                t1 = t2 = 0
                for k in range(n):
                    if k == i or k == j:
                        label[k] = 2
                    else:
                        point_z = point[k, :]
                        result = (point_x[0] - point_z[0]) * (point_y[1] - point_z[1]) - (point_x[1] - point_z[1]) * (point_y[0] - point_z[0])
                        if result >= 0:
                            label[k] = 1
                            t1 += 1
                        else:
                            label[k] = 0
                            t2 += 1
                if t1 <= 2 or t2 <= 2:
                    continue
                
                ind_up = npy.where(label > 0)
                ind_down = npy.where(label != 1)
                points_up = point[ind_up]
                points_down = point[ind_down]

                # Sort for each sub-pointset
                ind = sortConvexContourPoints(points_up[:, :2])
                ind_up = points_up[ind]
                i_ind_up = npy.where(ind_up[:, 2] == i)[0][0]
                j_ind_up = npy.where(ind_up[:, 2] == j)[0][0]
                if npy.abs(i_ind_up - j_ind_up) != 1 and npy.abs(i_ind_up - j_ind_up) != points_up.shape[0] - 1:
                    continue

                ind = sortConvexContourPoints(points_down[:, :2])
                ind_down = points_down[ind]
                i_ind_down = npy.where(ind_down[:, 2] == i)[0][0]
                j_ind_down = npy.where(ind_down[:, 2] == j)[0][0]
                if npy.abs(i_ind_down - j_ind_down) != 1 and npy.abs(i_ind_down - j_ind_down) != points_down.shape[0] - 1:
                    continue

                # Merge the sort results
                start_up = j_ind_up
                start_down = i_ind_down
                if (i_ind_up < j_ind_up and j_ind_up - i_ind_up == 1) or (j_ind_up == 0 and i_ind_up - j_ind_up > 1):
                    delta_up = 1
                else:
                    delta_up = -1
                if (i_ind_down < j_ind_down and j_ind_down - i_ind_down == 1) or (j_ind_down == 0 and i_ind_down - j_ind_down > 1):
                    delta_down = -1
                else:
                    delta_down = 1
                
                p = 0
                m = points_up.shape[0]
                while start_up != i_ind_up:
                    tmp_ind[p] = int(ind_up[start_up, 2])
                    p += 1
                    start_up = (start_up + delta_up + m) % m
                m = points_down.shape[0]
                while start_down != j_ind_down:
                    tmp_ind[p] = int(ind_down[start_down, 2])
                    p += 1
                    start_down = (start_down + delta_down + m) % m
                
                # Calculate the circumference of contour
                tmp_diff[:-1, :] = point_array[tmp_ind[1:], :2] - point_array[tmp_ind[:-1], :2]
                tmp_diff[-1, :] = point_array[tmp_ind[0], :2] - point_array[tmp_ind[-1], :2]
                tmp_dis = npy.sum(npy.hypot(tmp_diff[:, 0], tmp_diff[:, 1]))
                if tmp_dis < dis: # Find a shorter solution
                    dis = tmp_dis
                    result_ind = tmp_ind.copy()
                    flag = True

        if not flag: # Can't find the solution (Abnormal)
            return npy.arange(n, dtype = npy.uint8)

        return result_ind
