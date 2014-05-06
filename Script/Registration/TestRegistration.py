# -*- coding: utf-8 -*-
"""
Created on 2014-02-28

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
import itk, vtk
import SimpleITK as sitk
import util.RegistrationUtil as util

class TestRegistration(RegistrationBase):
    def __init__(self, gui):
        super(TestRegistration, self).__init__(gui)
    def getName(self):
        return 'Doing nothing'
    def register(self, fixedData, movingData, discard = False):
        fixed_points = fixedData.getPointSet('Contour')
        moving_points = movingData.getPointSet('Contour')
        
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
        
        # Get the result transformation parameters0
        T = ml.mat([0, 0, 0]).T;
        R = ml.mat([[1, 0, 0], 
                    [0, 1, 0], 
                    [0, 0, 1]]).I;
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        
        moving_points = movingData.getPointSet('Contour').copy()
        moving_center = movingData.getPointSet('Centerline').copy()                
        new_trans_points, result_center_points = util.resliceTheResultPoints(moving_points, moving_center, 20, moving_res, fixed_res, discard, R, T)
        
        T = -T
        T = R * T
        
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        return sitk.GetArrayFromImage(resultImage), {'Contour': trans_points, 'Centerline': result_center_points}, para + [0, 0, 0]
        
