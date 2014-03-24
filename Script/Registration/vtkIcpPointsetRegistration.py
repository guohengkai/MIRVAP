# -*- coding: utf-8 -*-
"""
Created on 2014-03-24

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
import itk, vtk
import SimpleITK as sitk

class vtkIcpPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(vtkIcpPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'ICP Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData):
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
            moving_delta = moving_bif - npy.min(moving_points[npy.where(npy.round(temp[:, 1]) == 0), 0])
            fixed_min = fixed_bif - moving_delta * moving_res[-1] / fixed_res[-1]
        
        fixed = fixed_points[npy.where(fixed_points[:, 2] >= fixed_min)]
        fixed = fixed[:, :3]
        moving = moving_points[:, :3]
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        
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
        result_source = icp_filter.GetOutput()
        
        n = result_source.GetNumberOfPoints()
        trans_points = npy.empty([n, 3], dtype = npy.float32)
        for i in range(n):
            temp = [0.0, 0.0, 0.0]
            result_source.GetPoint(i, temp)
            trans_points[i, :] = npy.array(temp)
        
        if (fixed_bif >= 0) and (moving_bif >= 0):
            trans_points[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
        trans_points[:, :3] /= fixed_res[:3]
        trans_points = npy.insert(trans_points, [trans_points.shape[1]], moving_points[:, -1].reshape(-1, 1), axis = 1)
        trans_points = npy.append(trans_points, npy.array([[-1, -1, -1, -1]]), axis = 0)
        
        matrix = icp.GetMatrix()
        T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T;
        R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                    [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                    [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I;
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            
        moving_center = movingData.getPointSet('Centerline').copy();
        result_center = moving_center[npy.where(moving_center[:, 0] >= 0)]
        result_center[:, :3] *= moving_res[:3]
        temp = ml.mat(result_center[:, :3]) * R + ml.ones((result_center.shape[0], 1)) * T.T
        
        result_center[:, :3] = temp
        result_center[:, :3] /= fixed_res[:3]
        result_center = npy.append(result_center, npy.array([[-1, -1, -1, -1]]), axis = 0)
        
        T = -T
        T = R * T
        
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        return sitk.GetArrayFromImage(resultImage), {'Contour': trans_points, 'Centerline': result_center}, para
