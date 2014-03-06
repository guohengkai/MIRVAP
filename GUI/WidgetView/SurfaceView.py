# -*- coding: utf-8 -*-
"""
Created on 2014-03-06

@author: Hengkai Guo
"""

from MIRVAP.Core.WidgetViewBase import WidgetViewBase
import vtk
import numpy as npy

class SurfaceView(WidgetViewBase):
    def __init__(self, parent = None):
        super(SurfaceView, self).__init__(parent)
        self.type = 'any'
    def getName(self):
        return "Surface View"
    def setWidgetView(self, widget):
        point_array = self.parent.getData().pointSet
        cnt = 0
        
        appendFilter = vtk.vtkAppendPolyData()
        
        for i in range(100, 150):
            data = point_array.getSlicePoint('Contour', 2, i)[cnt]
            if data is not None:
                count = data.shape[0]
                points = vtk.vtkPoints()
                points.SetNumberOfPoints(count)
                cells = vtk.vtkCellArray()
                cells.Allocate(1, count)
                cells.InsertNextCell(count)
                for j in range(count):
                    points.SetPoint(j, data[j, 0], data[j, 1], data[j, 2])
                    cells.InsertCellPoint(j)
                polydata = vtk.vtkPolyData()
                polydata.SetPoints(points)
                polydata.SetPolys(cells)
                appendFilter.AddInput(polydata)
                
        appendFilter.Update()
        
        contours = appendFilter.GetOutput()
        bounds = [0, 0, 0, 0, 0, 0]
        contours.GetBounds(bounds)
        origin = bounds[::2]
        spacing = [1, 1, 1]
        
        contour_point = contours.GetPoints()
        points = vtk.vtkPoints()
        count = contour_point.GetNumberOfPoints()
        points.SetNumberOfPoints(count)
        
        poly = vtk.vtkPolyData()
        for i in range(count):
            pt = [0, 0, 0]
            contour_point.GetPoint(i, pt)
            for j in range(3):
                pt[j] = int((pt[j] - origin[j]) / spacing[j] + 0.5)
            points.SetPoint(i, pt)
        poly.SetPolys(contours.GetPolys())
        poly.SetPoints(points)
        
        contour_to_surface = vtk.vtkVoxelContoursToSurfaceFilter()
        contour_to_surface.SetInput(poly)
        contour_to_surface.SetSpacing(spacing[0], spacing[1], spacing[2])
        contour_to_surface.Update()
        
        scaleCenter = [0, 0, 0]
        contour_to_surface.GetOutput().GetCenter(scaleCenter)
        scaleBounds = [0, 0, 0, 0, 0, 0]
        contour_to_surface.GetOutput().GetBounds(scaleBounds)
        center = [0, 0, 0]
        contours.GetCenter(center)
        
        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(contour_to_surface.GetOutputPort())
        transform = vtk.vtkTransform()
        transform_filter.SetTransform(transform)
        transform.Translate(-scaleCenter[0], -scaleCenter[1], -scaleCenter[2])
        transform.Scale((bounds[1] - bounds[0]) / (scaleBounds[1] - scaleBounds[0]),
                        (bounds[3] - bounds[2]) / (scaleBounds[3] - scaleBounds[2]),
                        (bounds[5] - bounds[4]) / (scaleBounds[5] - scaleBounds[4]))
        transform.Translate(center[0], center[1], center[2])
        
        mapper = vtk.vtkPolyDataMapper()
        #mapper.SetInputConnection(transform_filter.GetOutputPort())
        mapper.SetInput(contours)
        mapper.ScalarVisibilityOff()
        #mapper.ImmediateModeRenderingOn()
        
        contours_actor = vtk.vtkActor()
        contours_actor.SetMapper(mapper)
        contours_actor.GetProperty().SetRepresentationToWireframe()
        contours_actor.GetProperty().ShadingOff()
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window.SetInteractor(self.window_interactor)
        self.renderer.AddViewProp(contours_actor)
        
        self.window_interactor.Initialize()
        self.render_window.Render()
        
        # Manually set to trackball style
        self.window_interactor.SetKeyCode('t')
        self.window_interactor.CharEvent()
        self.window_interactor.GetInteractorStyle().AddObserver("KeyPressEvent", self.KeyPressCallback)
        self.window_interactor.GetInteractorStyle().AddObserver("CharEvent", self.KeyPressCallback)
    def KeyPressCallback(self, obj, event):
        pass
        
