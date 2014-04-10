# -*- coding: utf-8 -*-
"""
Created on 2014-03-16

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import MIRVAP.ThirdParty.gmmreg.executeGmmreg as eg
import numpy as npy
import numpy.matlib as ml
import itk
import SimpleITK as sitk

class GmmregPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(GmmregPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'GMMREG Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData):
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
            moving_delta = moving_bif - npy.min(moving_points[npy.where(npy.round(temp[:, 1]) == 0), 0])
            fixed_min = fixed_bif - moving_delta * moving_res[-1] / fixed_res[-1]
        
        fixed = fixed_points[npy.where(fixed_points[:, 2] >= fixed_min)]
        fixed = fixed[:, :3]
        moving = moving_points[:, :3]
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        
        eg.initial_data(fixed, moving)
        code = eg.run_executable()
        if code != 0:
            return None, None, None
        trans, para, para2 = eg.get_final_result()
        
        trans_points = trans;
        if (fixed_bif >= 0) and (moving_bif >= 0):
            trans_points[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        trans_points[:, :3] /= fixed_res[:3]
        trans_points = npy.insert(trans, [trans.shape[1]], moving_points[:, -1].reshape(-1, 1), axis = 1)
        trans_points = npy.append(trans_points, npy.array([[-1, -1, -1, -1]]), axis = 0)
        
        # Clear the temp files
        #eg.clear_temp_file()
        
        S1 = ml.ones([3, 3], dtype = npy.float32) * para2[3]
        C = npy.asmatrix(para2[:3]).T
        
        C2 = npy.asmatrix(para2[4:7]).T
        T0 = npy.asmatrix(para[4:]).T
        R = self.quaternion2rotation(para[:4])
        T = S1 * T0 + C2 - C
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        
        if index == 0:
            moving_center = movingData.getPointSet('Centerline').copy();
        else:
            moving_center = movingData.getPointSet('Contour').copy();
        result_center = moving_center[npy.where(moving_center[:, 0] >= 0)]
        result_center[:, :3] *= moving_res[:3]
        result_center[:, :3] -= C.T
        temp = ml.mat(result_center[:, :3]) * R + ml.ones((result_center.shape[0], 1)) * (T + C).T
        
        result_center[:, :3] = temp
        result_center[:, :3] /= fixed_res[:3]
        result_center = npy.append(result_center, npy.array([[-1, -1, -1, -1]]), axis = 0)
        
        T = -T
        T = R * T
        
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        transform.SetFixedParameters(C.T.tolist()[0])
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        if index == 0:
            return sitk.GetArrayFromImage(resultImage), {'Contour': trans_points, 'Centerline': result_center}, para
        else:
            return sitk.GetArrayFromImage(resultImage), {'Contour': result_center, 'Centerline': trans_points}, para
    def quaternion2rotation(self, q):
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
