# -*- coding: utf-8 -*-
"""
Created on 2014-05-01

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
import itk, vtk
import SimpleITK as sitk

class MRimageRegistration(RegistrationBase):
    def __init__(self, gui):
        super(MRimageRegistration, self).__init__(gui)
    def getName(self):
        return 'MR Images Simple Registration'
                                 
    def register(self, fixedData, movingData):
        clip1 = movingData.info.getData('clip')
        print clip1
        clip2 = fixedData.info.getData('clip')
        print clip2
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        print moving_res
        print fixed_res
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = [1, 0, 0, 0, 1, 0, 0, 0, 1, -clip1[4] * moving_res[0] + clip2[4] * fixed_res[0],
            -clip1[2] * moving_res[1] + clip2[2] * fixed_res[1], 0]
        transform.SetParameters(para)
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        return sitk.GetArrayFromImage(resultImage), {}, para + [0, 0, 0]
