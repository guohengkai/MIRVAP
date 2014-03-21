# -*- coding: utf-8 -*-
"""
Created on 2014-03-20

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.WidgetViewBase import WidgetViewBase
import vtk
import numpy as npy
from MIRVAP.GUI.MdiChild import MdiChildRegistration

# Only available when the vessel is along the z axis
class SurfaceView(WidgetViewBase):
    def __init__(self, parent = None):
        super(SurfaceView, self).__init__(parent)
        self.datatype = (3, )
    def getName(self):
        return "Surface View"
    def setWidgetView(self, widget, color = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
        super(SurfaceView, self).setWidgetView(widget)
        
        point_array_result = self.parent.getData().pointSet
        if type(self.parent) is MdiChildRegistration:
            point_array_move = self.parent.getData('move').pointSet
        else:
            point_array_move = point_array_result
        point_data_move = npy.array(point_array_move.getData('Contour'))
        point_data_result = npy.array(point_array_result.getData('Contour'))
        
        if point_data_result is None or not point_data_result.shape[0]:
            return
        zmin = int(npy.min(point_data_move[:, 2]) + 0.5)
        zmax = int(npy.max(point_data_move[:, 2]) + 0.5)
        #self.spacing = [1, 1, 1]
        self.spacing = self.parent.getData().getResolution().tolist()
        self.spacing = [float(x) / self.spacing[-1] for x in self.spacing]
        point_data_result[:, :2] *= self.spacing[:2]
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window.SetInteractor(self.window_interactor)
        
        self.contours = []
        self.delaunay3D = []
        #self.triangle_filter = []
        #self.smooth_filter = []
        self.delaunayMapper = []
        self.surface_actor = []
        
        for cnt in range(3):
            self.contours.append(vtk.vtkPolyData())
            self.delaunay3D.append(vtk.vtkDelaunay3D())
            #self.triangle_filter.append(vtk.vtkTriangleFilter())
            #self.smooth_filter.append(vtk.vtkButterflySubdivisionFilter())
            #self.smooth_filter.append(vtk.vtkLinearSubdivisionFilter())
            self.delaunayMapper.append(vtk.vtkDataSetMapper())
            self.surface_actor.append(vtk.vtkActor())
            
            point_result = point_data_result[npy.where(npy.round(point_data_result[:, -1]) == cnt)]
            point_move = point_data_move[npy.where(npy.round(point_data_move[:, -1]) == cnt)]
            if not point_result.shape[0]:
                continue
                
            self.cells = vtk.vtkCellArray()
            self.points = vtk.vtkPoints()
            l = 0
            for i in range(zmin, zmax + 1):
                data = point_result[npy.where(npy.round(point_move[:, 2]) == i)]
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
            #self.triangle_filter[cnt].SetInput(self.delaunay3D[cnt].GetOutput())
            #self.triangle_filter[cnt].PassVertsOn()
            #self.triangle_filter[cnt].PassLinesOn()
            #self.smooth_filter[cnt].SetInput(self.delaunay3D[cnt].GetOutput())
            #self.smooth_filter[cnt].SetInput(self.triangle_filter[cnt].GetOutput())
            #self.smooth_filter[cnt].SetNumberOfSubdivisions(3)
            
            self.delaunayMapper[cnt].SetInput(self.delaunay3D[cnt].GetOutput())
            
            self.surface_actor[cnt].SetMapper(self.delaunayMapper[cnt])
            self.surface_actor[cnt].GetProperty().SetDiffuseColor(color[cnt][0], color[cnt][1], color[cnt][2])
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
        
    def KeyPressCallback(self, obj, event):
        pass
        
