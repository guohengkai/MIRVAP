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
                                 
    def register(self, fixedData, movingData, index = -1, discard = False):
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
        
        moving_points = movingData.getPointSet('Contour').copy()
        moving_center = movingData.getPointSet('Centerline').copy()                
        new_trans_points, result_center_points = util.resliceTheResultPoints(moving_points, moving_center, 20, moving_res, fixed_res, discard, R, T, C)
        
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
        

