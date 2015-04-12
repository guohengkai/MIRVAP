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
from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis

class NonrigidIcpRegistration(RegistrationBase):
    def __init__(self, gui):
        super(NonrigidIcpRegistration, self).__init__(gui)
    def getName(self):
        return 'Nonrigid Labeled ICP Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData, index = -1, discard = False, delta = 0, fov = 9999999.0,
            down_fix = 1, down_mov = 1, occ = 9999999.0, useMask = False, isTime = False, MaxRate = 1,
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
        LandmarkTransform = vtk.vtkThinPlateSplineTransform()
        LandmarkTransform.SetBasisToR()
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
        
        # Resample the moving contour
        new_trans_points = movingData.getPointSet('Contour').copy()
        result_center_points = movingData.getPointSet('Centerline').copy()
        new_trans_points = new_trans_points[new_trans_points[:, 3] >= 0]
        result_center_points = result_center_points[result_center_points[:, 3] >= 0]
        
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
            
            for i in range(result_center_points.shape[0]):
                LandmarkTransform.InternalTransformPoint([result_center_points[i, 0], result_center_points[i, 1], result_center_points[i, 2]], p2)
                result_center_points[i, :3] = p2
            for i in range(new_trans_points.shape[0]):
                LandmarkTransform.InternalTransformPoint([new_trans_points[i, 0], new_trans_points[i, 1], new_trans_points[i, 2]], p2)
                new_trans_points[i, :3] = p2
                
            iternum += 1
            if iternum >= MaxIterNum:
                break
            
            for i in range(nb_points):
                a.GetPoint(i, p1)
                LandmarkTransform.InternalTransformPoint(p1, p2)
                b.SetPoint(i, p2)
            b, a = a, b
        time2 = time.time()
        
        if (fixed_bif >= 0) and (moving_bif >= 0):
            new_trans_points[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
            result_center_points[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
        resultImage = movingData.getData().copy()
        
        sa = SurfaceErrorAnalysis(None)
        dataset = db.BasicData(npy.array([[[0]]]), fixedData.getInfo(), {'Contour': new_trans_points, 'Centerline': result_center_points})
        mean_dis, mean_whole, max_dis, max_whole = sa.analysis(dataset, point_data_fix = fixed_points.copy(), useResult = True)
        del dataset
        print mean_dis
        print mean_whole
        
        if isTime:
            return resultImage, {'Contour': new_trans_points, 'Centerline': result_center_points}, [mean_dis, mean_whole], time2 - time1
        return resultImage, {'Contour': new_trans_points, 'Centerline': result_center_points}, [mean_dis, mean_whole]
