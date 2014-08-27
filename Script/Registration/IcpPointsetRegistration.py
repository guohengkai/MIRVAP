# -*- coding: utf-8 -*-
"""
Created on 2014-04-24

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

class IcpPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(IcpPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'ICP Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData, index = -1, discard = False, delta = 0, fov = 9999999.0, down = 1, occ = 9999999.0, op = False, useMask = False, isTime = False):
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
        #else:
            #temp = moving_points[:, 2:]
            #moving_delta = moving_bif - npy.min(temp[npy.where(npy.round(temp[:, 1]) == 0), 0])
            #fixed_min = fixed_bif - moving_delta * moving_res[-1] / fixed_res[-1]
        #print moving_res
        #print fixed_res
        
        # Augmentation of pointset
        #fixed = fixed_points[npy.where(fixed_points[:, 2] >= fixed_min)]
        fixed = fixed_points.copy()
        moving = moving_points.copy()
        if index == 0:
            fixed = util.augmentPointset(fixed, int(fixed_res[-1] / moving_res[-1] + 0.5), moving.shape[0], fixed_bif)
            moving = util.augmentPointset(moving, int(moving_res[-1] / fixed_res[-1] + 0.5), fixed.shape[0], moving_bif)
            #fixed = util.augmentPointset(fixed, int(fixed_res[-1] / moving_res[-1] + 0.5), moving.shape[0], fixed_bif, 8)
            #moving = util.augmentPointset(moving, int(moving_res[-1] / fixed_res[-1] + 0.5), fixed.shape[0], moving_bif, 8)
        '''
        if index == 1:
            fixed = util.augmentCenterline(fixed, fixed_res[-1] / moving_res[-1], 5)
            moving = util.augmentCenterline(moving, moving_res[-1] / fixed_res[-1], 5)
        '''
        #fixed = fixed[fixed[:, 2] != fixed_bif]
        #moving = moving[moving[:, 2] != moving_bif]
        #moving = moving[npy.cast[npy.int32](npy.abs(moving[:, 2] - moving_bif)) % down == 0]
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        #moving = moving[(npy.max(moving[:, 2]) - moving[:, 2] <= occ) | (moving[:, 2] - npy.min(moving[:, 2]) <= occ)]
        #moving = moving[npy.abs(moving[:, 2] - moving_bif * moving_res[2]) <= fov]
        #print moving.shape
        if (fixed_bif >= 0) and (moving_bif >= 0):
            fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
        #print fixed.shape[0], moving.shape[0]
        #return None, None, None
        
        # Prepare for ICP
        LandmarkTransform = vtk.vtkLandmarkTransform()
        LandmarkTransform.SetModeToRigidBody()
        MaxIterNum = 50
        MaxNum = 600
        
        targetPoints = [vtk.vtkPoints(), vtk.vtkPoints(), vtk.vtkPoints()]
        targetVertices = [vtk.vtkCellArray(), vtk.vtkCellArray(), vtk.vtkCellArray()]
        target = [vtk.vtkPolyData(), vtk.vtkPolyData(), vtk.vtkPolyData()]
        Locator = [vtk.vtkCellLocator(), vtk.vtkCellLocator(), vtk.vtkCellLocator()]
        if index == 0:
            if not op:
                label_dis = [3, 3, 3]
            else:
                label_dis = [3, 2, 1]
        else:
            if op:
                label_dis = [3, 3, 3]
            else:
                label_dis = [3, 2, 1]
            
        
        for i in range(3):
            for x in fixed[npy.round(fixed[:, 3]) != label_dis[i]]:
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
        '''
        j = 0
        k = 0
        temp = moving[moving[:, 3] == 0]
        step = 1
        if temp.shape[0] > MaxNum / 3:
            step = temp.shape[0] * 3 / MaxNum
        nb_points = temp.shape[0] / step
        for i in range(nb_points):
            points1.InsertNextPoint(temp[j][0], temp[j][1], temp[j][2])
            label[k] = 0
            j += step
            k += 1
        j = 0
        temp = moving[moving[:, 3] == 2]
        step = 1
        if temp.shape[0] > MaxNum / 3:
            step = temp.shape[0] * 3 / MaxNum
        nb_points = temp.shape[0] / step
        for i in range(nb_points):
            points1.InsertNextPoint(temp[j][0], temp[j][1], temp[j][2])
            label[k] = 2
            j += step
            k += 1
        j = 0
        temp = moving[moving[:, 3] == 1]
        step = 1
        if temp.shape[0] > MaxNum / 3:
            step = temp.shape[0] * 3 / MaxNum
        nb_points = temp.shape[0] / step
        for i in range(nb_points):
            points1.InsertNextPoint(temp[j][0], temp[j][1], temp[j][2])
            label[k] = 1
            j += step
            k += 1
        nb_points = k
        '''
        
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
        
        '''
        path = sys.argv[0]
        if os.path.isfile(path):
            path = os.path.dirname(path)
        path += '/Data/Transform'
        wfile = open("%s/transform.txt" % path, 'w')
        
        matrix = accumulate.GetMatrix()
        T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T;
        R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                    [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                    [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
        saveTransform(wfile, T, R)
        '''
        
        while True:
            for i in range(nb_points):
                Locator[label[i]].FindClosestPoint(a.GetPoint(i), outPoint, id1, id2, dist)
                closestp.SetPoint(i, outPoint)
                
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
            
            '''
            matrix = accumulate.GetMatrix()
            T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T;
            R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                        [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                        [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I;
            if (fixed_bif >= 0) and (moving_bif >= 0):
                T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2])
            saveTransform(wfile, T, R)
            '''
            b, a = a, b
        time2 = time.time()
        #wfile.close()
        # Get the result transformation parameters
        matrix = accumulate.GetMatrix()
        
        T = ml.mat([matrix.GetElement(0, 3), matrix.GetElement(1, 3), matrix.GetElement(2, 3)]).T;
        R = ml.mat([[matrix.GetElement(0, 0), matrix.GetElement(0, 1), matrix.GetElement(0, 2)], 
                    [matrix.GetElement(1, 0), matrix.GetElement(1, 1), matrix.GetElement(1, 2)], 
                    [matrix.GetElement(2, 0), matrix.GetElement(2, 1), matrix.GetElement(2, 2)]]).I
        
        #T = ml.mat([0, 0, 0]).T
        #R = ml.mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).T
        if (fixed_bif >= 0) and (moving_bif >= 0):
            T[2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2] + delta)
        
        # Resample the moving contour
        moving_points = movingData.getPointSet('Contour').copy()
        moving_center = movingData.getPointSet('Centerline').copy()
        #discard = True
        new_trans_points, result_center_points = util.resliceTheResultPoints(moving_points, moving_center, 20, moving_res, fixed_res, discard, R, T)
        
        T = -T
        T = R * T
        
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        '''
        import util.Hybrid.ElastixUtil as eutil
        fixed_points = fixedData.getPointSet('Contour').copy()
        fixed_points[:, :3] *= fixed_res
        fix_img_mask = eutil.getBinaryImageFromSegmentation(fixedData.getData(), fixed_points)
        result_points = new_trans_points.copy()
        result_points[:, :3] *= fixed_res
        result_img_mask = eutil.getBinaryImageFromSegmentation(sitk.GetArrayFromImage(resultImage), result_points)
        dice_index = eutil.calDiceIndexFromMask(fix_img_mask, result_img_mask)
        print dice_index
        del fix_img_mask
        del result_img_mask
        '''
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

