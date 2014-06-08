# -*- coding: utf-8 -*-
"""
Created on 2014-04-10

@author: Hengkai Guo
"""

from MIRVAP.Script.AnalysisBase import AnalysisBase
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCentroidFromContour
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_function import ac_mask
from MIRVAP.Script.Registration.util.RegistrationUtil import getPointsOntheSpline
import numpy as npy
import vtk

class AreaIndexAnalysis(AnalysisBase):
    def __init__(self, gui):
        super(AreaIndexAnalysis, self).__init__(gui)
    def getName(self):
        return 'Registration Area Index'
    def analysis(self, data, point_data_fix = None, area = False):
        if point_data_fix is None:
            point_data_fix = self.gui.dataModel[data.getFixedIndex()].getPointSet('Contour').copy()
        point_data_result = data.getPointSet('Contour').copy()
        image_size = image = data.getData()[0, :, :].transpose().shape
        self.spacing = data.getResolution().tolist()
        self.spacing[2] = 1.0 # The resolution of z axis is nothing to do with the analysis
        point_data_fix[:, :3] *= self.spacing[:3]
        point_data_result[:, :3] *= self.spacing[:3]
        
        cnt_num = npy.array([0, 0, 0])
        union_area = npy.array([0.0, 0.0, 0.0])
        total_area = npy.array([0.0, 0.0, 0.0])
        if area:
            mr_area = [0.0, 0.0, 0.0, 0.0]
            us_area = [0.0, 0.0, 0.0, 0.0]
        
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
                    #center_fix = npy.mean(data_fix[:, :2], axis = 0)
                    center_fix = calCentroidFromContour(data_fix[:, :2])[0]
                    #center_result = npy.mean(data_result[:, :2], axis = 0)
                    center_result = calCentroidFromContour(data_result[:, :2])[0]
                    points_fix = getPointsOntheSpline(data_fix, center_fix, data_fix.shape[0] * 10)[:, :2]
                    points_result = getPointsOntheSpline(data_result, center_result, data_result.shape[0] * 10)[:, :2]
                    
                    fix_mask = ac_mask(points_fix.transpose(), image_size)
                    result_mask = ac_mask(points_result.transpose(), image_size)
                    temp_fix_area = npy.sum(fix_mask)
                    temp_result_area = npy.sum(result_mask)
                    total_area[cnt] += temp_fix_area + temp_result_area
                    union_area[cnt] += npy.sum(fix_mask | result_mask)
                    if area:
                        mr_area[cnt] += temp_fix_area
                        mr_area[3] += temp_fix_area
                        us_area[cnt] += temp_result_area
                        us_area[3] += temp_result_area
                    
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
        
        if not area:
            return dice_index, dice_index_all
        else:
            for i in range(3):
                mr_area[i] /= cnt_num[i]
                us_area[i] /= cnt_num[i]
            mr_area[3] /= npy.sum(cnt_num)
            us_area[3] /= npy.sum(cnt_num)
            return dice_index, dice_index_all, mr_area, us_area
