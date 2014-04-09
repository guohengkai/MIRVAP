# -*- coding: utf-8 -*-
"""
Created on 2014-04-09

@author: Hengkai Guo
"""

from MIRVAP.Script.AnalysisBase import AnalysisBase
import numpy as npy
import vtk

class ContourErrorAnalysis(AnalysisBase):
    def __init__(self, gui):
        super(ContourErrorAnalysis, self).__init__(gui)
    def getName(self):
        return 'Mean Contour Registration Error'
    def analysis(self, data):
        point_data_fix = self.gui.dataModel[data.getFixedIndex()].getPointSet('Contour')
        point_data_result = data.getPointSet('Contour')
        self.spacing = data.getResolution().tolist()
        point_data_fix[:, :3] *= self.spacing[:3]
        point_data_result[:, :3] *= self.spacing[:3]
        
        cnt_num = npy.array([0, 0, 0])
        mean_dis = npy.array([0.0, 0.0, 0.0])
        max_dis = npy.array([0.0, 0.0, 0.0])
        
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
                    points_fix = getPointsOntheSpline(data_fix, center_fix)
                    points_result = getPointsOntheSpline(data_result, center_result)
                    
                    i = j = 0
                    for k in range(-44, 46):
                        angle = k * 4 / 180.0 * npy.pi
                        while points_fix[i, 2] < angle and i < 900:
                            i += 1
                        if i == 900 or (i > 0 and angle - points_fix[i - 1, 2] < points_fix[i, 2] - angle):
                            ind_fix = i - 1
                        else:
                            ind_fix = i
                        while points_result[j, 2] < angle and j < 900:
                            j += 1
                        if j == 900 or (j > 0 and angle - points_result[j - 1, 2] < points_result[j, 2] - angle):
                            ind_result = j - 1
                        else:
                            ind_result = j
                        temp_dis = npy.hypot(points_fix[ind_fix, 0] - points_result[ind_result, 0], points_fix[ind_fix, 1] - points_result[ind_result, 1])
                        max_dis[cnt] = npy.max([max_dis[cnt], temp_dis])
                        mean_dis[cnt] += temp_dis
                    
        mean_dis /= 90
        mean_whole = npy.sum(mean_dis)
        mean_dis /= cnt_num
        mean_dis[mean_dis != mean_dis] = 0 # Replace the NAN in the mean distance
        cnt_total = npy.sum(cnt_num)
        
        message = "Error on Vessel 0: %0.2fmm (Total %d slices)\nError on Vessel 1: %0.2fmm (Total %d slices)\nError on Vessel 2: %0.2fmm (Total %d slices)\nWhole Error: %0.2fmm (Total %d slices)\n" \
            % (mean_dis[0] + 0.005, cnt_num[0], mean_dis[1] + 0.005, cnt_num[1], mean_dis[2] + 0.005, cnt_num[2], mean_whole / cnt_total + 0.005, cnt_total) + \
            "-------------------------------------------------------\n" + \
            "Max Error on Vessel 0: %0.2fmm\nMax Error on Vessel 1: %0.2fmm\nMax Error on Vessel 2: %0.2fmm\nTotal Max Error: %0.2fmm" \
            % (max_dis[0], max_dis[1], max_dis[2], npy.max(max_dis));
        self.gui.showErrorMessage("Mean Registration Error", message)

def getPointsOntheSpline(data, center):
    count = data.shape[0]
    points = vtk.vtkPoints()
    for j in range(count):
        points.InsertPoint(j, data[j, 0], data[j, 1], 0)
    
    para_spline = vtk.vtkParametricSpline()
    para_spline.SetPoints(points)
    para_spline.ClosedOn()
    
    numberOfOutputPoints = 90 * 10
    result = npy.empty([numberOfOutputPoints, 3], dtype = npy.float32)
    
    for k in range(0, numberOfOutputPoints):
        t = k * 1.0 / numberOfOutputPoints
        pt = [0.0, 0.0, 0.0]
        para_spline.Evaluate([t, t, t], pt, [0] * 9)
        result[k, :2] = pt[:2]
        
    result[:, 2] = npy.arctan2(result[:, 1] - center[1], result[:, 0] - center[0])
    ind = result[:, 2].argsort()
    return result[ind, :]
