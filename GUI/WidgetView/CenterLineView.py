# -*- coding: utf-8 -*-
"""
Created on 2014-03-07

@author: Hengkai Guo
"""

from MIRVAP.Core.WidgetViewBase import WidgetViewBase
import vtk
import numpy as npy

class CenterLineView(WidgetViewBase):
    def __init__(self, parent = None):
        super(CenterLineView, self).__init__(parent)
        self.datatype = (3, )
    def getName(self):
        return "Centerline View"
    def setWidgetView(self, widget):
        super(CenterLineView, self).setWidgetView(widget)
        point_array = self.parent.getData().pointSet
        point_data = point_array.getData('Center')
        if point_data is None or not point_data.shape[0]:
            return
        
        #self.spacing = [1, 1, 1]
        self.spacing = self.parent.getData().getResolution().tolist()[::-1]
        self.spacing = [float(x) / self.spacing[-1] for x in self.spacing]
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window.SetInteractor(self.window_interactor)
        
        self.center = []
        self.center_mapper = []
        self.center_actor = []
        self.points = []
        self.para_spline = []
        self.spline_source = []
        
        for cnt in range(3):
            self.center.append(vtk.vtkPolyData())
            self.center_mapper.append(vtk.vtkPolyDataMapper())
            self.center_actor.append(vtk.vtkActor())
            self.points.append(vtk.vtkPoints())
            self.para_spline.append(vtk.vtkParametricSpline())
            self.spline_source.append(vtk.vtkParametricFunctionSource())
            
            point = point_data[npy.where(npy.round(point_data[:, -1]) == cnt)]
            point = point[point[:, 2].argsort(), :]
            count = point.shape[0]
            if not count:
                continue
                
            self.points[cnt].SetNumberOfPoints(count)
            for i in range(count):
                self.points[cnt].SetPoint(i, point[i, 0], point[i, 1], point[i, 2])
                
            self.para_spline[cnt].SetPoints(self.points[cnt])
            
            self.spline_source[cnt].SetParametricFunction(self.para_spline[cnt])
            numberOfOutputPoints = count * 10
            self.spline_source[cnt].SetUResolution(numberOfOutputPoints)
            
            self.center_mapper[cnt].SetInput(self.spline_source[cnt].GetOutput())
            self.center_mapper[cnt].ScalarVisibilityOff()
            
            self.center_actor[cnt].SetMapper(self.center_mapper[cnt])
            self.center_actor[cnt].SetScale(self.spacing)
            color = [0, 0, 0]
            color[cnt] = 1
            self.center_actor[cnt].GetProperty().SetColor(color[0], color[1], color[2])
            self.renderer.AddViewProp(self.center_actor[cnt])
            
        
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
        
