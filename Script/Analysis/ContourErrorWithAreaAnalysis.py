# -*- coding: utf-8 -*-
"""
Created on 2014-06-04

@author: Hengkai Guo
"""

from MIRVAP.Script.AnalysisBase import AnalysisBase
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCentroidFromContour
from MIRVAP.Script.Registration.util.RegistrationUtil import getPointsOntheSpline
import MIRVAP.Core.DataBase as db
import numpy as npy
import vtk

class ContourErrorWithAreaAnalysis(AnalysisBase):
    def __init__(self, gui):
        super(ContourErrorWithAreaAnalysis, self).__init__(gui)
    def getName(self):
        return 'Contour Registration Error With Area'
    def analysis(self, data, point_data_fix = None, all = False):
        if point_data_fix is None:
            point_data_fix = self.gui.dataModel[data.getFixedIndex()].getPointSet('Contour').copy()
        point_data_result = data.getPointSet('Contour').copy()
        self.spacing = data.getResolution().tolist()
        self.spacing[2] = 1.0 # The resolution of z axis is nothing to do with the analysis
        point_data_fix[:, :3] *= self.spacing[:3]
        point_data_result[:, :3] *= self.spacing[:3]
        
        cnt_num = npy.array([0, 0, 0])
        mean_dis = npy.array([0.0, 0.0, 0.0])
        max_dis = npy.array([0.0, 0.0, 0.0])
        square_sum_dis = npy.array([0.0, 0.0, 0.0])
        area_mr = npy.array([0.0, 0.0, 0.0])
        area_us = npy.array([0.0, 0.0, 0.0])
        if all:
            result = [{}, {}, {}]
            bif = db.getBifurcation(point_data_fix)
        
        for cnt in range(3):
            temp_result = point_data_result[npy.where(npy.round(point_data_result[:, -1]) == cnt)]
            temp_fix = point_data_fix[npy.where(npy.round(point_data_fix[:, -1]) == cnt)]
            if not temp_result.shape[0] or not temp_fix.shape[0]:
                continue
            zmin = int(npy.max([npy.min(temp_result[:, 2]), npy.min(temp_fix[:, 2])]) + 0.5)
            zmax = int(npy.min([npy.max(temp_result[:, 2]), npy.max(temp_fix[:, 2])]) + 0.5)
            
            for z in range(zmin, zmax + 1):
                data_fix = temp_fix[npy.where(npy.round(temp_fix[:, 2]) == z)]
                data_result = temp_result[npy.where(npy.round(temp_result[:, 2]) == z)]
                if data_fix is not None and data_result is not None:
                    if data_fix.shape[0] == 0 or data_result.shape[0] == 0:
                        continue
                    cnt_num[cnt] += 1
                    #center_fix = npy.mean(data_fix[:, :2], axis = 0)
                    center_fix, area_fix = calCentroidFromContour(data_fix[:, :2], True)
                    center_fix = center_fix[0]
                    area_mr[cnt] += area_fix
                    #center_result = npy.mean(data_result[:, :2], axis = 0)
                    center_result, area_result = calCentroidFromContour(data_result[:, :2], True)
                    center_result = center_result[0]
                    area_us[cnt] += area_result
                    points_fix = getPointsOntheSpline(data_fix, center_fix, 900)
                    points_result = getPointsOntheSpline(data_result, center_result, 900)
                    
                    i = j = 0
                    for k in range(-44, 46):
                        angle = k * 4 / 180.0 * npy.pi
                        while i < 900 and points_fix[i, 2] < angle:
                            i += 1
                        if i == 900 or (i > 0 and angle - points_fix[i - 1, 2] < points_fix[i, 2] - angle):
                            ind_fix = i - 1
                        else:
                            ind_fix = i
                        while j < 900 and points_result[j, 2] < angle:
                            j += 1
                        if j == 900 or (j > 0 and angle - points_result[j - 1, 2] < points_result[j, 2] - angle):
                            ind_result = j - 1
                        else:
                            ind_result = j
                        temp_dis = npy.hypot(points_fix[ind_fix, 0] - points_result[ind_result, 0], points_fix[ind_fix, 1] - points_result[ind_result, 1])
                        #temp_dis /= max([area_result / area_fix, area_fix / area_result])
                        max_dis[cnt] = npy.max([max_dis[cnt], temp_dis])
                        mean_dis[cnt] += temp_dis
                        square_sum_dis[cnt] += temp_dis ** 2
                        if all:
                            result[cnt][z - bif] = result[cnt].get(z - bif, 0) + temp_dis
                    #if all:
                        #result[cnt][z - bif] = area_result / area_fix
        
        cnt_total = npy.sum(cnt_num)
        sd = npy.sqrt(npy.max([(square_sum_dis - mean_dis ** 2 / (90 * cnt_num)) / (90 * cnt_num - 1), [0, 0, 0]], axis = 0))
        sd[sd != sd] = 0
        sd_all = npy.sqrt(npy.max([(npy.sum(square_sum_dis) - npy.sum(mean_dis) ** 2 / (90 * cnt_total)) / (90 * cnt_total - 1), 0]))
        
        mean_dis /= 90
        
        for cnt in range(3):
            if area_mr[cnt] < area_us[cnt]:
                rate = area_us[cnt] / area_mr[cnt]
            else:
                rate = area_us[cnt] / area_mr[cnt]
            mean_dis[cnt] /= rate
        
        #print area_us[0] / cnt_num[0], area_mr[0] / cnt_num[0]
        mean_whole = npy.sum(mean_dis)
        mean_dis /= cnt_num
        mean_dis[mean_dis != mean_dis] = 0 # Replace the NAN in the mean distance
        
        if self.gui is not None:
            message = "Error on Vessel 0: %0.2fmm (SD = %0.2fmm, Total %d slices)\nError on Vessel 1: %0.2fmm (SD = %0.2fmm, Total %d slices)\nError on Vessel 2: %0.2fmm (SD = %0.2fmm, Total %d slices)\nWhole Error: %0.2fmm (SD = %0.2fmm, Total %d slices)\n" \
                % (mean_dis[0], sd[0], cnt_num[0], mean_dis[1], sd[1], cnt_num[1], mean_dis[2], sd[2], cnt_num[2], mean_whole / cnt_total, sd_all, cnt_total) + \
                "-----------------------------------------------------------------------------\n" + \
                "Max Error on Vessel 0: %0.2fmm\nMax Error on Vessel 1: %0.2fmm\nMax Error on Vessel 2: %0.2fmm\nTotal Max Error: %0.2fmm" \
                % (max_dis[0], max_dis[1], max_dis[2], npy.max(max_dis));
            self.gui.showErrorMessage("Contour Registration Error", message)
            
        if not all:
            return mean_dis, mean_whole / cnt_total, max_dis, npy.max(max_dis)
        else:
            for cnt in range(3):
                for x in result[cnt].keys():
                    result[cnt][x] /= 90
            return mean_dis, mean_whole / cnt_total, max_dis, npy.max(max_dis), result

