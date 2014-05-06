# -*- coding: utf-8 -*-
"""
Created on 2014-03-24

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

class vtkIcpPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(vtkIcpPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'ICP Pointset Registration For Vessel(vtk)'
                                 
    def register(self, fixedData, movingData, discard = False):
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
        #print moving_res
        #print fixed_res
        
        # Augmentation of pointset
        fixed = fixed_points[npy.where(fixed_points[:, 2] >= fixed_min)]
        moving = moving_points.copy()
        fixed = util.augmentPointset(fixed, int(fixed_res[-1] / moving_res[-1] + 0.5), moving.shape[0], fixed_bif)
        moving = util.augmentPointset(moving, int(moving_res[-1] / fixed_res[-1] + 0.5), fixed.shape[0], moving_bif)
        
        fixed = fixed[:, :3]
        moving = moving[:, :3]
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        print fixed.shape[0], moving.shape[0]
        #return None, None, None
        
        sourcePoints = vtk.vtkPoints()
        sourceVertices = vtk.vtkCellArray()
        for x in moving:
            id = sourcePoints.InsertNextPoint(x[0], x[1], x[2])
            sourceVertices.InsertNextCell(1)
            sourceVertices.InsertCellPoint(id)
        source = vtk.vtkPolyData()
        source.SetPoints(sourcePoints)
        source.SetVerts(sourceVertices)
        
        targetPoints = vtk.vtkPoints()
        targetVertices = vtk.vtkCellArray()
        for x in fixed:
            id = targetPoints.InsertNextPoint(x[0], x[1], x[2])
            targetVertices.InsertNextCell(1)
            targetVertices.InsertCellPoint(id)
        target = vtk.vtkPolyData()
        target.SetPoints(targetPoints)
        target.SetVerts(targetVertices)
        
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(source)
        icp.SetTarget(target)
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.Modified()
        icp.Update()
        
        icp_filter = vtk.vtkTransformPolyDataFilter()
        icp_filter.SetInput(source)
        icp_filter.SetTransform(icp)
        icp_filter.Update()
        
        # Get the result transformation parameters
        matrix = icp.GetMatrix()
        T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T;
        R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                    [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                    [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I;
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
            
