# -*- coding: utf-8 -*-
"""
Created on 2014-03-16

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCentroidFromContour
import MIRVAP.Core.DataBase as db
import MIRVAP.ThirdParty.gmmreg.executeGmmreg as eg
import numpy as npy
import numpy.matlib as ml
import itk, vtk
import SimpleITK as sitk
import util.RegistrationUtil as util

class GmmregPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(GmmregPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'GMMREG Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData, index = -1):
        if index == -1:
            index = self.gui.getDataIndex({'Contour': 0, 'Centerline': 1}, 'Select the object')
        if index is None:
            return None, None, None
        if index == 0:
            fixed_points = fixedData.getPointSet('Contour')
            moving_points = movingData.getPointSet('Contour')
        else:
            fixed_points = fixedData.getPointSet('Centerline')
            moving_points = movingData.getPointSet('Centerline')
        
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        fixed_points = fixed_points.copy()[npy.where(fixed_points[:, 0] >= 0)]
        moving_points = moving_points.copy()[npy.where(moving_points[:, 0] >= 0)]
        # Use the bifurcation as the initial position
        fixed_bif = db.getBifurcation(fixed_points)
        moving_bif = db.getBifurcation(moving_points)
        if (fixed_bif < 0) or (moving_bif < 0):
            fixed_min = 0
        else:
            temp = moving_points[:, 2:]
            moving_delta = moving_bif - npy.min(temp[npy.where(npy.round(temp[:, 1]) == 0), 0])
            fixed_min = fixed_bif - moving_delta * moving_res[-1] / fixed_res[-1]
        #fixed_min = 0
        
        # Augmentation of pointset
        fixed = fixed_points[npy.where(fixed_points[:, 2] >= fixed_min)]
        moving = moving_points.copy()
        if index == 0:
            fixed = util.augmentPointset(fixed, int(fixed_res[-1] / moving_res[-1] + 0.5), moving.shape[0], fixed_bif)
            moving = util.augmentPointset(moving, int(moving_res[-1] / fixed_res[-1] + 0.5), fixed.shape[0], moving_bif)
        
        fixed = fixed[:, :3]
        moving = moving[:, :3]
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        #print fixed.shape[0], moving.shape[0]
        
        '''
        MaxNum = 200
        step = 1
        if moving.shape[0] > MaxNum:
            step = moving.shape[0] / MaxNum
        moving = moving[::step, :]
        '''
        
        eg.initial_data(fixed, moving)
        code = eg.run_executable()
        if code != 0:
            return None, None, None
        trans, para, para2 = eg.get_final_result()
        
        # Clear the temp files
        #eg.clear_temp_file()
        
        # Get the result transformation parameters
        S1 = ml.eye(3, dtype = npy.float32) * para2[3]
        C = npy.asmatrix(para2[:3]).T
        
        C2 = npy.asmatrix(para2[4:7]).T
        T0 = npy.asmatrix(para[4:]).T
        R = util.quaternion2rotation(para[:4])
        T = S1 * T0 + C2 - C
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        
        # Resample the moving contour
        resampled_points = [None, None, None]
        moving_points = movingData.getPointSet('Contour').copy()
        for cnt in range(3):
            temp_result = moving_points[npy.where(npy.round(moving_points[:, -1]) == cnt)]
            if not temp_result.shape[0]:
                continue
            zmin = int(npy.min(temp_result[:, 2]) + 0.5)
            zmax = int(npy.max(temp_result[:, 2]) + 0.5)
            resampled_points[cnt] = npy.zeros([(zmax - zmin + 1) * 10, 4], dtype = npy.float32)
            resampled_index = 0
            
            for z in range(zmin, zmax + 1):
                data_result = temp_result[npy.where(npy.round(temp_result[:, 2]) == z)]
                if data_result is not None:
                    if data_result.shape[0] == 0:
                        continue
                    
                    #center_result = npy.mean(data_result[:, :2], axis = 0)
                    center_result = calCentroidFromContour(data_result[:, :2])[0]
                    points_result = util.getPointsOntheSpline(data_result, center_result, 900)
                    
                    i = 0
                    for k in range(-4, 6):
                        angle = k * 36 / 180.0 * npy.pi
                        
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
                        
        # Apply the transformation on the resampled points
        for cnt in range(3):
            resampled_points[cnt][:, :3] *= moving_res[:3]
            resampled_points[cnt][:, :3] -= C.T
            temp = ml.mat(resampled_points[cnt][:, :3]) * R + ml.ones((resampled_points[cnt].shape[0], 1)) * (T + C).T
            
            resampled_points[cnt][:, :3] = temp
            resampled_points[cnt][:, :3] /= fixed_res[:3]
        
        # Reslice the result points
        trans_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        for cnt in range(3):
            zmin = int(npy.ceil(npy.max(resampled_points[cnt][:10, 2])))
            zmax = int(npy.min(resampled_points[cnt][-10:, 2]))
            
            for k in range(0, 10):
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
                        trans_points = npy.append(trans_points, [[new_point[0], new_point[1], znow, cnt]], axis = 0)
                        znow += 1
                        if znow > zmax:
                            break
                    old_pt = pt
        
        moving_center = movingData.getPointSet('Centerline').copy()
        result_center_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        if moving_center.shape[0] > 1:
            result_center = moving_center[npy.where(moving_center[:, 0] >= 0)]
            result_center[:, :3] *= moving_res[:3]
            result_center[:, :3] -= C.T
            temp = ml.mat(result_center[:, :3]) * R + ml.ones((result_center.shape[0], 1)) * (T + C).T
            result_center[:, :3] = temp
            result_center[:, :3] /= fixed_res[:3]
            
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
        
        T = -T
        T = R * T
        
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        transform.SetFixedParameters(C.T.tolist()[0])
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        return sitk.GetArrayFromImage(resultImage), {'Contour': trans_points, 'Centerline': result_center_points}, para + C.T.tolist()[0]
        

