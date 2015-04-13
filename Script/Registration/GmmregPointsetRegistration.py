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
import util.Hybrid.GmmregUtil as gutil
import time

class GmmregPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(GmmregPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'GMMREG Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData, index = -1, discard = False, method = "EM_TPS", execute = True, isTime = False):
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
        time1 = time.time()
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        fixed_points = fixed_points.copy()[npy.where(fixed_points[:, -1] >= 0)]
        moving_points = moving_points.copy()[npy.where(moving_points[:, -1] >= 0)]
        # Use the bifurcation as the initial position
        fixed_bif = db.getBifurcation(fixed_points)
        moving_bif = db.getBifurcation(moving_points)
        if (fixed_bif < 0) or (moving_bif < 0):
            fixed_min = 0
        else:
            temp = moving_points[:, 2:]
            moving_delta = moving_bif - npy.min(temp[npy.where(npy.round(temp[:, 1]) == 0), 0])
        #fixed_min = 0
        
        # Augmentation of pointset
        fixed = fixed_points.copy()
        tmp_fix = fixedData.getPointSet('Centerline')
        tmp_fix = tmp_fix[tmp_fix[:, -1] >= 0].copy()
        ctrl_pts = gutil.getControlPoints(tmp_fix, 1.0 / fixed_res[2])
        moving = moving_points.copy()
        
        fixed = fixed[:, :3]
        moving = moving[:, :3]
        fixed[:, :3] *= fixed_res[:3]
        ctrl_pts *= fixed_res[:3]
        ctrl_pts_backup = ctrl_pts.copy()
        moving[:, :3] *= moving_res[:3]
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            ctrl_pts[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        #print fixed.shape[0], moving.shape[0]
        
        eg.initial_data(fixed, moving, ctrl_pts)
        
        if execute:
            code = eg.run_executable(method = method)
            #print code
            if code != 0:
                print "GMM Fail!"
                return None, None, None
        
        trans, para, para2 = eg.get_final_result(methodname = method)
        time2 = time.time()
        
        # Clear the temp files
        #eg.clear_temp_file()
        
        # Get the result transformation parameters
        if method == 'rigid':
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
            #new_trans_points, result_center_points = util.resliceTheResultPoints(moving_points, moving_center, 20, moving_res, fixed_res, discard, R, T, C)
            new_trans_points = util.applyTransformForPoints(moving_points, moving_res, fixed_res, R, T, C)
            result_center_points = util.applyTransformForPoints(moving_center, moving_res, fixed_res, R, T, C)
            
            
            T = -T
            T = R * T
            
            """
            # Copy the output points of GMMREG for test
            new_trans_points = trans
            
            if (fixed_bif >= 0) and (moving_bif >= 0):
                new_trans_points[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
                
            new_trans_points[:, :3] /= fixed_res[:3]
            new_trans_points = npy.insert(new_trans_points, [new_trans_points.shape[1]], moving_points[:, -1].reshape(-1, 1), axis = 1)
            new_trans_points = npy.append(new_trans_points, npy.array([[-1, -1, -1, -1]]), axis = 0)
            #result_center_points = movingData.getPointSet('Centerline').copy()
            result_center_points = movingData.getPointSet('Contour').copy()  
            """
            
            transform = sitk.Transform(3, sitk.sitkAffine)
            para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
            transform.SetParameters(para)
            transform.SetFixedParameters(C.T.tolist()[0])
            
            #movingImage = movingData.getSimpleITKImage()
            #fixedImage = fixedData.getSimpleITKImage()
            #resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
            
            if isTime:
                #return sitk.GetArrayFromImage(resultImage), {'Contour': new_trans_points, 'Centerline': result_center_points}, para + C.T.tolist()[0], time2 - time1
                return movingData.getData().copy(), {'Contour': new_trans_points, 'Centerline': result_center_points}, para + C.T.tolist()[0], time2 - time1
            #return sitk.GetArrayFromImage(resultImage), {'Contour': new_trans_points, 'Centerline': result_center_points}, para + C.T.tolist()[0]
            return movingData.getData().copy(), {'Contour': new_trans_points, 'Centerline': result_center_points}, para + C.T.tolist()[0]
            
        else: # EM_TPS
            moving_points = movingData.getPointSet('Contour').copy()
            moving_points = moving_points[npy.where(moving_points[:, 0] >= 0)]
            moving = moving_points[:, :3].copy()
            moving *= moving_res[:3]
            m = moving.shape[0]
            n = ctrl_pts.shape[0]
            
            M = ml.mat(moving.copy())
            
            C2 = npy.asmatrix(para2[4:7])
            C2 = ml.repmat(C2, m, 1)
            
            C3 = npy.asmatrix(para2[7:])
            C3 = ml.repmat(C3, n, 1)
            ctrl_pts -= C3
            ctrl_pts /= para2[3]
            
            C = npy.asmatrix(para2[:3])
            C = ml.repmat(C, m, 1)
            moving -= C
            moving /= para2[3]
            
            basis = ml.zeros([m, n], dtype = npy.float32)
            basis[:, 0] = 1
            basis[:, 1:4] = moving
            
            U = gutil.ComputeTPSKernel(moving, ctrl_pts)
            basis[:, 4:] = U * ml.mat(trans)
            #print npy.array(basis)
            
            T = basis * ml.mat(para)
            T *= para2[3]
            T += C2 - C
            
            
            if (fixed_bif >= 0) and (moving_bif >= 0):
                T[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            
            M += T
            new_trans_points = npy.array(M).copy()
            new_trans_points[:, :3] /= fixed_res[:3]
            new_trans_points = npy.insert(new_trans_points, [new_trans_points.shape[1]], moving_points[:, -1].reshape(-1, 1), axis = 1)
            new_trans_points = npy.append(new_trans_points, npy.array([[-1, -1, -1, -1]]), axis = 0)
            
            moving_points = movingData.getPointSet('Centerline').copy()
            moving_points = moving_points[npy.where(moving_points[:, 0] >= 0)]
            moving = moving_points[:, :3].copy()
            moving *= moving_res[:3]
            m = moving.shape[0]

            M = ml.mat(moving.copy())
            
            C2 = npy.asmatrix(para2[4:7])
            C2 = ml.repmat(C2, m, 1)
            
            C = npy.asmatrix(para2[:3])
            C = ml.repmat(C, m, 1)
            moving -= C
            moving /= para2[3]
            
            basis = ml.zeros([m, n], dtype = npy.float32)
            basis[:, 0] = 1
            basis[:, 1:4] = moving
            
            U = gutil.ComputeTPSKernel(moving, ctrl_pts)
            basis[:, 4:] = U * ml.mat(trans)
            #print npy.array(basis)
            
            T = basis * ml.mat(para)
            T *= para2[3]
            T += C2 - C
            
            if (fixed_bif >= 0) and (moving_bif >= 0):
                T[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            
            M += T
            result_center_points = npy.array(M).copy()
            result_center_points[:, :3] /= fixed_res[:3]
            result_center_points = npy.insert(result_center_points, [result_center_points.shape[1]], moving_points[:, -1].reshape(-1, 1), axis = 1)
            result_center_points = npy.append(result_center_points, npy.array([[-1, -1, -1, -1]]), axis = 0)
            #print result_center_points
            
            moving = ctrl_pts_backup.copy()
            m = moving.shape[0]
            M = ml.mat(moving.copy())
            
            C = npy.asmatrix(para2[:3])
            C = ml.repmat(C, m, 1)
            moving -= C
            moving /= para2[3]

            C2 = npy.asmatrix(para2[4:7])
            C2 = ml.repmat(C2, m, 1)
            
            basis = ml.zeros([m, n], dtype = npy.float32)
            basis[:, 0] = 1
            basis[:, 1:4] = moving
            
            U = gutil.ComputeTPSKernel(moving, ctrl_pts)
            basis[:, 4:] = U * ml.mat(trans)
            #print npy.array(basis)
            
            T = basis * ml.mat(para)
            T *= para2[3]
            T += C2 - C
            
            if (fixed_bif >= 0) and (moving_bif >= 0):
                T[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            
            M += T
            result_ctrl = npy.array(M).copy()
            #print result_ctrl
            
            image_type = fixedData.getITKImageType()
            transform_type = itk.ThinPlateSplineKernelTransform.D3
            transform = transform_type.New()
            pointset_type = itk.PointSet.PD33S
            source_pointset = pointset_type.New()
            target_pointset = pointset_type.New()
            count = 0
            for point in ctrl_pts_backup:
                tmp_point = itk.Point.D3()
                tmp_point[0] = point[0]
                tmp_point[1] = point[1]
                tmp_point[2] = point[2]
                source_pointset.SetPoint(count, tmp_point)
                count += 1
            count = 0
            for point in ctrl_pts_backup:
                tmp_point = itk.Point.D3()
                tmp_point[0] = point[0]
                tmp_point[1] = point[1]
                tmp_point[2] = point[2]
                target_pointset.SetPoint(count, tmp_point)
                count += 1
                
            transform.SetSourceLandmarks(source_pointset)
            transform.SetTargetLandmarks(target_pointset)
            transform.ComputeWMatrix()
            
            """
            # Test for TPS Transform
            moving_points = movingData.getPointSet('Centerline').copy()
            moving_points = moving_points[npy.where(moving_points[:, 0] >= 0)]
            moving = moving_points[:, :3].copy()
            moving *= moving_res[:3]
            for point in moving:
                tmp_point = itk.Point.D3()
                tmp_point[0] = point[0]
                tmp_point[1] = point[1]
                tmp_point[2] = point[2]
                rst_point = transform.TransformPoint(tmp_point)
                point[0] = rst_point[0]
                point[1] = rst_point[1]
                point[2] = rst_point[2]
            moving /= fixed_res[:3]
            print moving
            """
            
#            image_type = fixedData.getITKImageType()
#            resampler = itk.ResampleImageFilter[image_type, image_type].New()
#            movingImage = movingData.getITKImage()
#            fixedImage = fixedData.getITKImage()
#            
#            resampler.SetTransform(transform)
#            resampler.SetInput(movingImage)
#            
#            region = fixedImage.GetLargestPossibleRegion()
#            
#            resampler.SetSize(region.GetSize())
#            resampler.SetOutputSpacing(fixedImage.GetSpacing())
#            resampler.SetOutputDirection(fixedImage.GetDirection())
#            resampler.SetOutputOrigin(fixedImage.GetOrigin())
#            resampler.SetDefaultPixelValue(0)
#            resampler.Update()
#        
#            outputImage = resampler.GetOutput()
#            image = itk.PyBuffer[image_type].GetArrayFromImage(outputImage)
            if isTime:
                return movingData.getData().copy(), {'Contour': new_trans_points, 'Centerline': result_center_points}, [0, 0, 0], time2 - time1
            return movingData.getData().copy(), {'Contour': new_trans_points, 'Centerline': result_center_points}, [0, 0, 0]
        
