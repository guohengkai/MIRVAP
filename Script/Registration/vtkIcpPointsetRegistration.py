# -*- coding: utf-8 -*-
"""
Created on 2014-03-24

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
from scipy import interpolate
import itk, vtk
import SimpleITK as sitk

class vtkIcpPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(vtkIcpPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'ICP Pointset Registration For Vessel'
                                 
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
        moving = moving_points[:, :3].copy()
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
        
        # Get the result transformation parameters
        matrix = icp.GetMatrix()
        T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T;
        R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                    [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                    [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I;
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            
        # Resample the moving contour
        resampled_points = [None, None, None]
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
                    
                    center_result = npy.mean(data_result[:, :2], axis = 0)
                    points_result = getPointsOntheSpline(data_result, center_result, 900)
                    
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
            temp = ml.mat(resampled_points[cnt][:, :3]) * R + ml.ones((resampled_points[cnt].shape[0], 1)) * T.T
            
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
                points = vtk.vtkPoints()
                for i in range(count):
                    points.InsertPoint(i, data[i, 0], data[i, 1], data[i, 2])
        
                para_spline = vtk.vtkParametricSpline()
                para_spline.SetPoints(points)
                para_spline.ClosedOff()
                
                #zmin = int(npy.ceil(resampled_points[cnt][0, 2]))
                #zmax = int(resampled_points[cnt][-1, 2])
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
        
        if index == 0:
            moving_center = movingData.getPointSet('Centerline').copy();
        else:
            moving_center = movingData.getPointSet('Contour').copy();
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
        
        if index == 0:
            return sitk.GetArrayFromImage(resultImage), {'Contour': trans_points, 'Centerline': result_center}, para
        else:
            return sitk.GetArrayFromImage(resultImage), {'Contour': result_center, 'Centerline': trans_points}, para
            
def getPointsOntheSpline(data, center, numberOfOutputPoints):
    if data.shape[0] >= 4:
        # Sort the pointSet for a convex contour
        point = npy.delete(data, 2, axis = 1)
        core = point.mean(axis = 0)
        point -= core
        angle = npy.arctan2(point[:, 1], point[:, 0])
        ind = angle.argsort()
        data[:, :] = data[ind, :]
        
    count = data.shape[0]
    points = vtk.vtkPoints()
    for j in range(count):
        points.InsertPoint(j, data[j, 0], data[j, 1], 0)
    
    para_spline = vtk.vtkParametricSpline()
    para_spline.SetPoints(points)
    para_spline.ClosedOn()
    
    result = npy.empty([numberOfOutputPoints, 3], dtype = npy.float32)
    
    for k in range(0, numberOfOutputPoints):
        t = k * 1.0 / numberOfOutputPoints
        pt = [0.0, 0.0, 0.0]
        para_spline.Evaluate([t, t, t], pt, [0] * 9)
        result[k, :2] = pt[:2]
        
    result[:, 2] = npy.arctan2(result[:, 1] - center[1], result[:, 0] - center[0])
    ind = result[:, 2].argsort()
    return result[ind, :]
