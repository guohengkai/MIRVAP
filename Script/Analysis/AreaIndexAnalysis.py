# -*- coding: utf-8 -*-
"""
Created on 2014-04-10

@author: Hengkai Guo
"""

from MIRVAP.Script.AnalysisBase import AnalysisBase
import numpy as npy
import vtk

class AreaIndexAnalysis(AnalysisBase):
    def __init__(self, gui):
        super(AreaIndexAnalysis, self).__init__(gui)
    def getName(self):
        return 'Registration Area Index'
    def analysis(self, data, point_data_fix = None):
        if point_data_fix is None:
            point_data_fix = self.gui.dataModel[data.getFixedIndex()].getPointSet('Contour').copy()
        point_data_result = data.getPointSet('Contour').copy()
        self.spacing = data.getResolution().tolist()
        self.spacing[2] = 1.0 # The resolution of z axis is nothing to do with the analysis
        point_data_fix[:, :3] *= self.spacing[:3]
        point_data_result[:, :3] *= self.spacing[:3]
        
        cnt_num = npy.array([0, 0, 0])
        union_area = npy.array([0.0, 0.0, 0.0])
        total_area = npy.array([0.0, 0.0, 0.0])
        
        for cnt in range(3):
            temp_result = point_data_result[npy.where(npy.round(point_data_result[:, -1]) == cnt)]
            temp_fix = point_data_fix[npy.where(npy.round(point_data_fix[:, -1]) == cnt)]
            if not temp_result.shape[0] or not temp_fix.shape[0]:
                continue
            zmin = int(npy.min([npy.min(temp_result[:, 2]), npy.min(temp_fix[:, 2])]) + 0.5)
            zmax = int(npy.max([npy.max(temp_result[:, 2]), npy.max(temp_fix[:, 2])]) + 0.5)
            
            for z in range(zmin, zmax + 1):
                data_fix = temp_fix[npy.where(npy.round(temp_fix[:, 2]) == z)]
                data_result = temp_result[npy.where(npy.round(temp_result[:, 2]) == z)]
                if data_fix is not None and data_result is not None:
                    if data_fix.shape[0] == 0 or data_result.shape[0] == 0:
                        continue
                    cnt_num[cnt] += 1
                    center_fix = npy.mean(data_fix[:, :2], axis = 0)
                    center_result = npy.mean(data_result[:, :2], axis = 0)
                    points_fix = getPointsOntheSpline(data_fix, center_fix, data_fix.shape[0] * 10)[:, :2]
                    points_result = getPointsOntheSpline(data_result, center_result, data_result.shape[0] * 10)[:, :2]
                    
                    xmax = int(npy.max([npy.max(data_result[:, 0]), npy.max(data_fix[:, 0])]) + 0.5) + 2
                    xmin = npy.max([int(npy.min([npy.min(data_result[:, 0]), npy.min(data_fix[:, 0])]) + 0.5) - 2, 0])
                    ymax = int(npy.max([npy.max(data_result[:, 1]), npy.max(data_fix[:, 1])]) + 0.5) + 2
                    ymin = npy.max([int(npy.min([npy.min(data_result[:, 1]), npy.min(data_fix[:, 1])]) + 0.5) - 2, 0])
                    fix_mask = getMaskFromPoints(points_fix, xmin, xmax, ymin, ymax, center_fix)
                    result_mask = getMaskFromPoints(points_result, xmin, xmax, ymin, ymax, center_result)
                    temp_fix_area = npy.sum(fix_mask)
                    temp_result_area = npy.sum(result_mask)
                    total_area[cnt] += temp_fix_area + temp_result_area
                    union_area[cnt] += npy.sum(fix_mask | result_mask)
                    
        intersect_area = total_area - union_area
        jaccard_index = intersect_area / union_area
        dice_index = 2 * intersect_area / total_area
        jaccard_index_all = npy.sum(intersect_area) / npy.sum(union_area)
        dice_index_all = 2 * npy.sum(intersect_area) / npy.sum(total_area)
        # Replace the NAN
        jaccard_index[jaccard_index != jaccard_index] = 0
        dice_index[dice_index != dice_index] = 0
        
        if self.gui is not None:
            message = "Jaccard Index on Vessel 0: %0.3f\nJaccard Index on Vessel 1: %0.3f\nJaccard Index on Vessel 2: %0.3f\nTotal Jaccard Index: %0.3f\n" \
                % (jaccard_index[0], jaccard_index[1], jaccard_index[2], jaccard_index_all) + \
                "-------------------------------------------------------\n" + \
                "Dice Index on Vessel 0: %0.3f\nDice Index on Vessel 1: %0.3f\nDice Index on Vessel 2: %0.3f\nTotal Dice Index: %0.3f" \
                % (dice_index[0], dice_index[1], dice_index[2], dice_index_all);
            self.gui.showErrorMessage("Registration Area Index", message)
        
        return dice_index, dice_index_all

# Use BFS to fill the contour, a little slow
def getMaskFromPoints(points, xmin, xmax, ymin, ymax, center):
    h = xmax - xmin + 1
    w = ymax - ymin + 1
    mask = npy.zeros([h, w], dtype = npy.int8)
    
    points[:, 0] -= xmin
    points[:, 1] -= ymin
    center[0] -= xmin
    center[1] -= ymin
    points = npy.append(points, [[points[0, 0], points[0, 1]]], axis = 0)
    
    for i in range(points.shape[0] - 1):
        p = points[i + 1, :] - points[i, :]
        if npy.abs(p[0]) >= npy.abs(p[1]):
            k = p[1] / p[0]
            if p[0] > 0:
                x, y = points[i, :]
                xend = points[i + 1, 0]
            else:
                x, y = points[i + 1, :]
                xend = points[i, 0]
            while x <= xend:
                mask[int(x + 0.5), int(y + 0.5)] = 1
                y += k
                x += 1
        else:
            k = p[0] / p[1]
            if p[1] > 0:
                x, y = points[i, :]
                yend = points[i + 1, 1]
            else:
                x, y = points[i + 1, :]
                yend = points[i, 1]
            while y <= yend:
                mask[int(x + 0.5), int(y + 0.5)] = 1
                x += k
                y += 1
    
    center_x = int(center[0])
    center_y = int(center[1])
    d = npy.array([[1, 0], [0, -1], [0, 1], [-1, 0]])
    queue = npy.zeros([h * w, 2], dtype = npy.int32)
    head = -1
    tail = 0
    queue[tail, :] = [center_x, center_y]
    mask[queue[tail, 0], queue[tail, 1]] = 1
    
    while True:
        head += 1
        
        for dd in d:
            temp = queue[head, :] + dd
            if mask[temp[0], temp[1]]:
                continue
            tail += 1
            queue[tail, :] = temp
            mask[queue[tail, 0], queue[tail, 1]] = 1
        if head >= tail:
            break
    
    return mask

def getPointsOntheSpline(data, center, numberOfOutputPoints):
    if data.shape[0] >= 4:
        # Sort the pointSet for a convex contour
        point = npy.delete(data, 2, axis = 1)
        core = point.mean(axis = 0)
        point -= core
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
