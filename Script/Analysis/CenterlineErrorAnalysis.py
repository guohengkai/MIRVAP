# -*- coding: utf-8 -*-
"""
Created on 2014-04-27

@author: Hengkai Guo
"""

from MIRVAP.Script.AnalysisBase import AnalysisBase
import numpy as npy
import vtk

class CenterlineErrorAnalysis(AnalysisBase):
    def getName(self):
        return 'Centerline Registration Error'
    def analysis(self, data, point_data_fix = None):
        if point_data_fix is None:
            point_data_fix = self.gui.dataModel[data.getFixedIndex()].getPointSet('Centerline').copy()
        point_data_result = data.getPointSet('Centerline').copy()
        
        self.spacing = data.getResolution().tolist()
        point_data_fix = point_data_fix[point_data_fix[:, 0] >= 0]
        point_data_result = point_data_result[point_data_result[:, 0] >= 0]
        point_data_fix[:, :3] *= self.spacing[:3]
        point_data_result[:, :3] *= self.spacing[:3]
        
        fix_center_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        ind = point_data_fix[:, 2].argsort()
        point_data_fix = point_data_fix[ind]
        
        Locator = [vtk.vtkCellLocator(), vtk.vtkCellLocator(), vtk.vtkCellLocator()]
        targetPoints = [vtk.vtkPoints(), vtk.vtkPoints(), vtk.vtkPoints()]
        targetVertices = [vtk.vtkCellArray(), vtk.vtkCellArray(), vtk.vtkCellArray()]
        target = [vtk.vtkPolyData(), vtk.vtkPolyData(), vtk.vtkPolyData()]
        
        for cnt in range(1, 3):
            resampled_points = point_data_fix[npy.where(npy.round(point_data_fix[:, -1]) != 3 - cnt)]
            
            count = resampled_points.shape[0]
            points = vtk.vtkPoints()
            for i in range(count):
                if i + 1 < count and resampled_points[i, 3] != resampled_points[i + 1, 3]: # bifurcation point
                    continue
                points.InsertPoint(i, resampled_points[i, 0], resampled_points[i, 1], resampled_points[i, 2])
    
            para_spline = vtk.vtkParametricSpline()
            para_spline.SetPoints(points)
            para_spline.ClosedOff()
            
            numberOfOutputPoints = count * 50
            
            for i in range(0, numberOfOutputPoints):
                t = i * 1.0 / numberOfOutputPoints
                pt = [0.0, 0.0, 0.0]
                para_spline.Evaluate([t, t, t], pt, [0] * 9)
                id = targetPoints[0].InsertNextPoint(pt[0], pt[1], pt[2])
                targetVertices[0].InsertNextCell(1)
                targetVertices[0].InsertCellPoint(id)
                id = targetPoints[cnt].InsertNextPoint(pt[0], pt[1], pt[2])
                targetVertices[cnt].InsertNextCell(1)
                targetVertices[cnt].InsertCellPoint(id)
        
        for i in range(3):
            target[i].SetPoints(targetPoints[i])
            target[i].SetVerts(targetVertices[i])
            
            Locator[i].SetDataSet(target[i])
            Locator[i].SetNumberOfCellsPerBucket(1)
            Locator[i].BuildLocator()
        
        id1 = id2 = vtk.mutable(0)
        dist = vtk.mutable(0.0)
        outPoint = [0.0, 0.0, 0.0]
        
        cnt_num = npy.array([0, 0, 0])
        mean_dis = npy.array([0.0, 0.0, 0.0])
        max_dis = npy.array([0.0, 0.0, 0.0])
        
        for pt in point_data_result:
            cnt = int(pt[-1] + 0.5)
            Locator[cnt].FindClosestPoint(pt[:3].tolist(), outPoint, id1, id2, dist)
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
