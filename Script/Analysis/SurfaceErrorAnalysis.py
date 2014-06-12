# -*- coding: utf-8 -*-
"""
Created on 2014-06-04

@author: Hengkai Guo
"""

from MIRVAP.Script.AnalysisBase import AnalysisBase
import MIRVAP.Script.Registration.util.RegistrationUtil as util
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
import vtk

class SurfaceErrorAnalysis(AnalysisBase):
    def getName(self):
        return 'Surface Registration Error'
    def analysis(self, data, point_data_fix = None, point_data_mov = None, spacing_mov = None):
        if point_data_fix is None:
            point_data_fix = self.gui.dataModel[data.getFixedIndex()].getPointSet('Contour').copy()
            point_data_mov = self.gui.dataModel[data.getMovingIndex()].getPointSet('Contour').copy()
            spacing_mov = self.gui.dataModel[data.getMovingIndex()].getResolution().tolist()
        
        self.spacing = data.getResolution().tolist()
        point_data_fix = point_data_fix[point_data_fix[:, 0] >= 0]
        point_data_mov = point_data_mov[point_data_mov[:, 0] >= 0]
        bif = db.getBifurcation(point_data_fix)
        point_data_fix = util.augmentPointset(point_data_fix, 3, -1, bif, nn = 20)
        point_data_fix[:, :3] *= self.spacing[:3]
        point_data_mov[:, :3] *= spacing_mov[:3]
        
        para = data.info.getData('transform')
        R = ml.mat(para[:9]).reshape(3, 3)
        T = ml.mat(para[9:12]).T
        T = R.I * T
        T = -T
        point_data_mov[:, :3] = util.applyTransformForPoints(point_data_mov[:, :3], npy.array([1.0, 1, 1]), npy.array([1.0, 1, 1]), R, T)
        
        Locator = vtk.vtkCellLocator()
        targetPoints = vtk.vtkPoints()
        targetVertices = vtk.vtkCellArray()
        target = vtk.vtkPolyData()
        
        for x in point_data_fix:
            id = targetPoints.InsertNextPoint(x[0], x[1], x[2])
            targetVertices.InsertNextCell(1)
            targetVertices.InsertCellPoint(id)
        
        target.SetPoints(targetPoints)
        target.SetVerts(targetVertices)
        
        Locator.SetDataSet(target)
        Locator.SetNumberOfCellsPerBucket(1)
        Locator.BuildLocator()
        
        id1 = id2 = vtk.mutable(0)
        dist = vtk.mutable(0.0)
        outPoint = [0.0, 0.0, 0.0]
        
        cnt_num = npy.array([0, 0, 0])
        mean_dis = npy.array([0.0, 0.0, 0.0])
        max_dis = npy.array([0.0, 0.0, 0.0])
        
        for pt in point_data_mov:
            cnt = int(pt[-1] + 0.5)
            Locator.FindClosestPoint(pt[:3].tolist(), outPoint, id1, id2, dist)
            dis = npy.sqrt(npy.sum((npy.array(outPoint) - pt[:3]) ** 2))
            mean_dis[cnt] += dis
            max_dis[cnt] = npy.max([max_dis[cnt], dis])
            cnt_num[cnt] += 1
        
        cnt_total = npy.sum(cnt_num)
        mean_whole = npy.sum(mean_dis) / cnt_total
        mean_dis /= cnt_num
        mean_dis[mean_dis != mean_dis] = 0 # Replace the NAN in the mean distance
        max_whole = npy.max(max_dis)
        
        if self.gui is not None:
            message = "Error on Vessel 0: %0.2fmm (Total %d slices)\nError on Vessel 1: %0.2fmm (Total %d slices)\nError on Vessel 2: %0.2fmm (Total %d slices)\nWhole Error: %0.2fmm (Total %d slices)\n" \
                % (mean_dis[0], cnt_num[0], mean_dis[1], cnt_num[1], mean_dis[2], cnt_num[2], mean_whole, cnt_total) + \
                "-----------------------------------------------------------------------------\n" + \
                "Max Error on Vessel 0: %0.2fmm\nMax Error on Vessel 1: %0.2fmm\nMax Error on Vessel 2: %0.2fmm\nTotal Max Error: %0.2fmm" \
                % (max_dis[0], max_dis[1], max_dis[2], npy.max(max_dis));
            self.gui.showErrorMessage("Centerline Registration Error", message)
        return mean_dis, mean_whole, max_dis, max_whole
