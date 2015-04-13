# -*- coding: utf-8 -*-
"""
Created on 2015-03-05

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCentroidFromContour
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
from scipy import interpolate
import itk, vtk
import SimpleITK as sitk
import util.RegistrationUtil as util
import sys, os
import time
import copy

class WeightIcpRegistration(RegistrationBase):
    def __init__(self, gui):
        super(WeightIcpRegistration, self).__init__(gui)
    def getName(self):
        return 'Weighted Labeled ICP Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData, index = -1, discard = False, delta = 0, fov = 9999999.0,
            down_fix = 1, down_mov = 1, occ = 9999999.0, useMask = False, isTime = False, MaxRate = 0.2,
            aug = False, distance_fix = 0.3, distance_mov = 0.1, w_wrong = 1.5):
        time1 = time.time()
        if index == -1:
            index = self.gui.getDataIndex({'Contour': 0, 'Centerline': 1}, 'Select the object')
        if index is None:
            return None, None, None
        if index == 0:
            fixed_points = fixedData.getPointSet('Contour').copy()
            moving_points = movingData.getPointSet('Contour').copy()
        else:
            fixed_points = fixedData.getPointSet('Centerline').copy()
            moving_points = movingData.getPointSet('Centerline').copy()
        
        fixed_bif = db.getBifurcation(fixed_points)
        moving_bif = db.getBifurcation(moving_points)
        
        if useMask:
            mask_points = movingData.getPointSet('Mask')
            for point in mask_points:
                moving_points = npy.delete(moving_points, npy.where((npy.abs(moving_points[:, 2] - point[2]) < 0.0001) & (npy.round(moving_points[:, -1]) == point[3])), axis = 0)
            
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        fixed_points = fixed_points[npy.where(fixed_points[:, 0] >= 0)]
        moving_points = moving_points[npy.where(moving_points[:, 0] >= 0)]
        
        # Use the bifurcation as the initial position
        if (fixed_bif < 0) or (moving_bif < 0):
            fixed_min = 0
        
        # Augmentation of pointset
        fixed = fixed_points.copy()
        moving = moving_points.copy()
        
        if index == 1 and aug:
            fixed = util.augmentCenterline(fixed, 1, 10)
            moving = util.augmentCenterline(moving, 1, 10)
            fix_dis = util.getAxisSin(fixed, 3 / fixed_res[2]) * distance_fix
            mov_dis = util.getAxisSin(moving, 3 / moving_res[2]) * distance_mov
            fixed = util.resampleCenterline(fixed, fix_dis / fixed_res[2])
            moving = util.resampleCenterline(moving, mov_dis / moving_res[2])
        
        fixed = fixed[npy.cast[npy.int32](npy.abs(fixed[:, 2] - fixed_bif)) % down_fix == 0]
        moving = moving[npy.cast[npy.int32](npy.abs(moving[:, 2] - moving_bif)) % down_mov == 0]
        
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
        
        # Prepare for ICP
        LandmarkTransform = vtk.vtkLandmarkTransform()
        LandmarkTransform.SetModeToRigidBody()
        MaxIterNum = 50
        #MaxNum = 600
        MaxNum = int(MaxRate * moving.shape[0] + 0.5)
        
        targetPoints = [vtk.vtkPoints(), vtk.vtkPoints(), vtk.vtkPoints()]
        targetVertices = [vtk.vtkCellArray(), vtk.vtkCellArray(), vtk.vtkCellArray()]
        target = [vtk.vtkPolyData(), vtk.vtkPolyData(), vtk.vtkPolyData()]
        Locator = [vtk.vtkCellLocator(), vtk.vtkCellLocator(), vtk.vtkCellLocator()]
        
        for i in range(3):
            for x in fixed[npy.round(fixed[:, 3]) == i]:
                id = targetPoints[i].InsertNextPoint(x[0], x[1], x[2])
                targetVertices[i].InsertNextCell(1)
                targetVertices[i].InsertCellPoint(id)
            target[i].SetPoints(targetPoints[i])
            target[i].SetVerts(targetVertices[i])
            
            Locator[i].SetDataSet(target[i])
            Locator[i].SetNumberOfCellsPerBucket(1)
            Locator[i].BuildLocator()
        
        step = 1
        if moving.shape[0] > MaxNum:
            ind = moving[:, 2].argsort()
            moving = moving[ind, :]
            step = moving.shape[0] / MaxNum
        nb_points = moving.shape[0] / step
        
        accumulate = vtk.vtkTransform()
        accumulate.PostMultiply()
        
        points1 = vtk.vtkPoints()
        points1.SetNumberOfPoints(nb_points)
        
        label = npy.zeros([MaxNum * 2], dtype = npy.int8)
        
        j = 0
        for i in range(nb_points):
            points1.SetPoint(i, moving[j][0], moving[j][1], moving[j][2])
            label[i] = moving[j][3]
            j += step
        
        closestp = vtk.vtkPoints()
        closestp.SetNumberOfPoints(nb_points)
        points2 = vtk.vtkPoints()
        points2.SetNumberOfPoints(nb_points)
        
        id1 = id2 = vtk.mutable(0)
        dist = vtk.mutable(0.0)
        outPoint = [0.0, 0.0, 0.0]
        p1 = [0.0, 0.0, 0.0]
        p2 = [0.0, 0.0, 0.0]
        iternum = 0
        a = points1
        b = points2
        w_mat = [[1, w_wrong, w_wrong], [w_wrong, 1, 99999999], [w_wrong, 99999999, 1]]
        
        while True:
            for i in range(nb_points):
                min_dist = 99999999
                min_outPoint = [0.0, 0.0, 0.0]
                for j in range(3):
                    Locator[j].FindClosestPoint(a.GetPoint(i), outPoint, id1, id2, dist)
                    dis = npy.sqrt(npy.sum((npy.array(outPoint) - a.GetPoint(i)) ** 2))
                    if dis * w_mat[label[i]][j] < min_dist:
                        min_dist = dis * w_mat[label[i]][j]
                        min_outPoint = copy.deepcopy(outPoint)
                    
                closestp.SetPoint(i, min_outPoint)
                
            LandmarkTransform.SetSourceLandmarks(a)
            LandmarkTransform.SetTargetLandmarks(closestp)
            LandmarkTransform.Update()
            
            accumulate.Concatenate(LandmarkTransform.GetMatrix())
            
            iternum += 1
            if iternum >= MaxIterNum:
                break
            
            for i in range(nb_points):
                a.GetPoint(i, p1)
                LandmarkTransform.InternalTransformPoint(p1, p2)
                b.SetPoint(i, p2)
            b, a = a, b
        time2 = time.time()
        
        # Get the result transformation parameters
        matrix = accumulate.GetMatrix()
        
        T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T
        R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                    [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                    [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I
        
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
        
        # Resample the moving contour
        moving_points = movingData.getPointSet('Contour').copy()
        moving_center = movingData.getPointSet('Centerline').copy()
        new_trans_points, result_center_points = moving_points, moving_center
        result_center_points[:, :3] = util.applyTransformForPoints(result_center_points[:, :3], moving_res, fixed_res, R, T, ml.zeros([3, 1], dtype = npy.float32))
        new_trans_points[:, :3] = util.applyTransformForPoints(new_trans_points[:, :3], moving_res, fixed_res, R, T, ml.zeros([3, 1], dtype = npy.float32))
        T = -T
        T = R * T
        
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        if isTime:
            return sitk.GetArrayFromImage(resultImage), {'Contour': new_trans_points, 'Centerline': result_center_points}, para + [0, 0, 0], time2 - time1
        return sitk.GetArrayFromImage(resultImage), {'Contour': new_trans_points, 'Centerline': result_center_points}, para + [0, 0, 0]
            
def saveTransform(wfile, T, R):
    for i in range(3):
        wfile.write("%f " % T[i, 0])
    for i in range(3):
        for j in range(3):
            wfile.write("%f " % R[i, j])
    wfile.write("\n")

