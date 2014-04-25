# -*- coding: utf-8 -*-
"""
Created on 2014-04-25

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.WidgetViewBase import WidgetViewBase
import vtk
import numpy as npy
import numpy.matlib as ml
from MIRVAP.GUI.MdiChild import MdiChildRegistration
import sys, os

# Only available when the vessel is along the z axis
class SurfaceGifView(WidgetViewBase):
    def __init__(self, parent = None):
        super(SurfaceGifView, self).__init__(parent)
        self.datatype = (3, )
        self.type = 'registration'
    def getName(self):
        return "Surface Gif View"
    def setWidgetView(self, widget):
        super(SurfaceGifView, self).setWidgetView(widget)
        
        self.point_array_move = self.parent.getData('move').pointSet
        self.point_data_move = npy.array(self.point_array_move.getData('Contour'))
        self.point_array_fix = self.parent.getData('fix').pointSet
        self.point_data_fix = npy.array(self.point_array_fix.getData('Contour'))
        
        if self.point_data_move is None or not self.point_data_move.shape[0]:
            return
        if self.point_data_fix is None or not self.point_data_fix.shape[0]:
            return
        
        #self.spacing = [1, 1, 1]
        self.spacing = self.parent.getData().getResolution().tolist()
        self.spacing_move = self.parent.getData('move').getResolution().tolist()
        self.tmp_space = self.spacing[-1]
        self.spacing = [float(x) / self.tmp_space for x in self.spacing]
        #point_data_move[:, :2] *= self.spacing_move[:2]
        self.point_data_fix[:, :2] *= self.spacing[:2]
        self.zmin = int(npy.min(self.point_data_fix[:, 2]) + 0.5)
        self.zmax = int(npy.max(self.point_data_fix[:, 2]) + 0.5)
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window.SetInteractor(self.window_interactor)
        
        self.contours = []
        self.delaunay3D = []
        self.delaunayMapper = []
        self.surface_actor = []
        
        for cnt in range(3):
            self.contours.append(vtk.vtkPolyData())
            self.delaunay3D.append(vtk.vtkDelaunay3D())
            self.delaunayMapper.append(vtk.vtkDataSetMapper())
            self.surface_actor.append(vtk.vtkActor())
            
            point_fix = self.point_data_fix[npy.where(npy.round(self.point_data_fix[:, -1]) == cnt)]
            if not point_fix.shape[0]:
                continue
                
            self.cells = vtk.vtkCellArray()
            self.points = vtk.vtkPoints()
            l = 0
            for i in range(self.zmin, self.zmax + 1):
                data = point_fix[npy.where(npy.round(point_fix[:, 2]) == i)]
                if data is not None:
                    if data.shape[0] == 0:
                        continue
                    count = data.shape[0]
                    points = vtk.vtkPoints()
                    for j in range(count):
                        points.InsertPoint(j, data[j, 0], data[j, 1], data[j, 2])
                    
                    para_spline = vtk.vtkParametricSpline()
                    para_spline.SetPoints(points)
                    para_spline.ClosedOn()
                    
                    # The number of output points set to 10 times of input points
                    numberOfOutputPoints = count * 10
                    self.cells.InsertNextCell(numberOfOutputPoints)
                    for k in range(0, numberOfOutputPoints):
                        t = k * 1.0 / numberOfOutputPoints
                        pt = [0.0, 0.0, 0.0]
                        para_spline.Evaluate([t, t, t], pt, [0] * 9)
                        if pt[0] != pt[0]:
                            print pt
                            continue
                        self.points.InsertPoint(l, pt[0], pt[1], pt[2])
                        self.cells.InsertCellPoint(l)
                        l += 1

            self.contours[cnt].SetPoints(self.points)
            self.contours[cnt].SetPolys(self.cells)
            
            self.delaunay3D[cnt].SetInput(self.contours[cnt])
            self.delaunay3D[cnt].SetAlpha(2)
            
            self.delaunayMapper[cnt].SetInput(self.delaunay3D[cnt].GetOutput())
            
            self.surface_actor[cnt].SetMapper(self.delaunayMapper[cnt])
            self.surface_actor[cnt].GetProperty().SetDiffuseColor(0, 0, 1)
            self.surface_actor[cnt].GetProperty().SetSpecularColor(1, 1, 1)
            self.surface_actor[cnt].GetProperty().SetSpecular(0.4)
            self.surface_actor[cnt].GetProperty().SetSpecularPower(50)
            
            self.renderer.AddViewProp(self.surface_actor[cnt])
        
        self.renderer.ResetCamera()
        point = self.renderer.GetActiveCamera().GetFocalPoint()
        dis = self.renderer.GetActiveCamera().GetDistance()
        self.renderer.GetActiveCamera().SetViewUp(0, 0, 1)
        self.renderer.GetActiveCamera().SetPosition(point[0], point[1] - dis, point[2])
        self.renderer.ResetCameraClippingRange()
        self.render_window.Render()
        
        # Manually set to trackball style
        self.window_interactor.SetKeyCode('t')
        self.window_interactor.CharEvent()
        self.window_interactor.GetInteractorStyle().AddObserver("KeyPressEvent", self.KeyPressCallback)
        self.window_interactor.GetInteractorStyle().AddObserver("CharEvent", self.KeyPressCallback)
        
        self.tmp_data_move = npy.array(self.point_data_move)
        self.tmp_data_move[:, :3] *= self.spacing_move[:3]
        
        self.spacing_move = [float(x) / self.spacing_move[-1] for x in self.spacing_move]
        self.point_data_move[:, :2] *= self.spacing_move[:2]
        self.zmin = int(npy.min(self.point_data_move[:, 2]) + 0.5)
        self.zmax = int(npy.max(self.point_data_move[:, 2]) + 0.5)
        
        self.point_data_result = self.point_data_move
        
        for cnt in range(3, 6):
            self.contours.append(vtk.vtkPolyData())
            self.delaunay3D.append(vtk.vtkDelaunay3D())
            self.delaunayMapper.append(vtk.vtkDataSetMapper())
            self.surface_actor.append(vtk.vtkActor())
            
            point_result = self.point_data_result[npy.where(npy.round(self.point_data_result[:, -1]) == cnt - 3)]
            point_move = self.point_data_move[npy.where(npy.round(self.point_data_move[:, -1]) == cnt - 3)]
            if not point_result.shape[0]:
                continue
                
            self.cells = vtk.vtkCellArray()
            self.points = vtk.vtkPoints()
            l = 0
            for i in range(self.zmin, self.zmax + 1):
                data = point_result[npy.where(npy.round(point_move[:, 2]) == i)]
                if data is not None:
                    if data.shape[0] == 0:
                        continue
                    count = data.shape[0]
                    points = vtk.vtkPoints()
                    for j in range(count):
                        points.InsertPoint(j, data[j, 0], data[j, 1], data[j, 2])
                    
                    para_spline = vtk.vtkParametricSpline()
                    para_spline.SetXSpline(vtk.vtkKochanekSpline())
                    para_spline.SetYSpline(vtk.vtkKochanekSpline())
                    para_spline.SetZSpline(vtk.vtkKochanekSpline())
                    para_spline.SetPoints(points)
                    para_spline.ClosedOn()
                    
                    # The number of output points set to 10 times of input points
                    numberOfOutputPoints = count * 10
                    self.cells.InsertNextCell(numberOfOutputPoints)
                    for k in range(0, numberOfOutputPoints):
                        t = k * 1.0 / numberOfOutputPoints
                        pt = [0.0, 0.0, 0.0]
                        para_spline.Evaluate([t, t, t], pt, [0] * 9)
                        if pt[0] != pt[0]:
                            print pt
                            continue
                        self.points.InsertPoint(l, pt[0], pt[1], pt[2])
                        self.cells.InsertCellPoint(l)
                        l += 1

            self.contours[cnt].SetPoints(self.points)
            self.contours[cnt].SetPolys(self.cells)
            
            self.delaunay3D[cnt].SetInput(self.contours[cnt])
            self.delaunay3D[cnt].SetAlpha(2)
            
            self.delaunayMapper[cnt].SetInput(self.delaunay3D[cnt].GetOutput())
            
            self.surface_actor[cnt].SetMapper(self.delaunayMapper[cnt])
            self.surface_actor[cnt].GetProperty().SetDiffuseColor(1, 0, 0)
            self.surface_actor[cnt].GetProperty().SetSpecularColor(1, 1, 1)
            self.surface_actor[cnt].GetProperty().SetSpecular(0.4)
            self.surface_actor[cnt].GetProperty().SetSpecularPower(50)
            
            self.renderer.AddViewProp(self.surface_actor[cnt])
        
        self.render_window.Render()
        #point_data_result = applyTransform(tmp_data_move, npy.array([25.043671, -4.149676, 96.002946, 
        #        0.318970, 0.947765, 0.000293, -0.916973, 0.308529, 0.252926, 0.239623, -0.080945, 0.967486]))
        
        
    def KeyPressCallback(self, obj, event):
        ch = self.window_interactor.GetKeySym()
        if ch == 'Return':
            trans = loadTransform()
            num = 0
            for transform in trans:
                self.point_data_result = applyTransform(self.tmp_data_move, transform)
                self.point_data_result[:, :3] /= self.tmp_space
                for cnt in range(3, 6):
                    point_result = self.point_data_result[npy.where(npy.round(self.point_data_result[:, -1]) == cnt - 3)]
                    point_move = self.point_data_move[npy.where(npy.round(self.point_data_move[:, -1]) == cnt - 3)]
                    if not point_result.shape[0]:
                        continue
                        
                    self.cells = vtk.vtkCellArray()
                    self.points = vtk.vtkPoints()
                    l = 0
                    for i in range(self.zmin, self.zmax + 1):
                        data = point_result[npy.where(npy.round(point_move[:, 2]) == i)]
                        if data is not None:
                            if data.shape[0] == 0:
                                continue
                            count = data.shape[0]
                            points = vtk.vtkPoints()
                            for j in range(count):
                                points.InsertPoint(j, data[j, 0], data[j, 1], data[j, 2])
                            
                            para_spline = vtk.vtkParametricSpline()
                            para_spline.SetXSpline(vtk.vtkKochanekSpline())
                            para_spline.SetYSpline(vtk.vtkKochanekSpline())
                            para_spline.SetZSpline(vtk.vtkKochanekSpline())
                            para_spline.SetPoints(points)
                            para_spline.ClosedOn()
                            
                            # The number of output points set to 10 times of input points
                            numberOfOutputPoints = count * 10
                            self.cells.InsertNextCell(numberOfOutputPoints)
                            for k in range(0, numberOfOutputPoints):
                                t = k * 1.0 / numberOfOutputPoints
                                pt = [0.0, 0.0, 0.0]
                                para_spline.Evaluate([t, t, t], pt, [0] * 9)
                                if pt[0] != pt[0]:
                                    print pt
                                    continue
                                self.points.InsertPoint(l, pt[0], pt[1], pt[2])
                                self.cells.InsertCellPoint(l)
                                l += 1
        
                    self.contours[cnt].SetPoints(self.points)
                    self.contours[cnt].SetPolys(self.cells)
                    self.contours[cnt].Update()
                    
                self.render_window.Render()
                saveGif(self.render_window, num)
                num += 1
        
def applyTransform(points, para):
    T = ml.mat(para[:3]).T;
    R = ml.mat(para[3:].reshape(3, 3)).T.I;
    result = npy.array(points)
    result[:, :3] = ml.mat(points[:, :3]) * R + ml.ones((points.shape[0], 1)) * T.T
    return result
def loadTransform():
    path = sys.argv[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
    path += '/Data/Transform/transform_37L.txt'
    return npy.loadtxt(path)
def saveGif(window, n):
    path = sys.argv[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
    path += '/Data/Gif/img%d.jpg' % n
            
    window_image_filter = vtk.vtkWindowToImageFilter()
    writer = vtk.vtkJPEGWriter()
    window_image_filter.SetInput(window)
    window_image_filter.Update()
    
    writer.SetInputConnection(window_image_filter.GetOutputPort())
    writer.SetFileName(path)
    writer.Write()
