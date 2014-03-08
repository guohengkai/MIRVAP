# -*- coding: utf-8 -*-
"""
Created on 2014-02-26

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.PluginBase import PluginBase
import vtk
import numpy as npy
import MIRVAP.Core.DataBase as db

class ClipPlugin(PluginBase):
    '''
        Left button:          Choose the bound of clip (Disable to change the window level)
        Press Enter Key:      Apply the clip on the data
    '''
    def __init__(self):
        super(ClipPlugin, self).__init__()
        self.X1 = self.Y1 = self.X2 = self.Y2 = 0
        
    def enable(self, parent):
        self.parent = parent
        
        self.pts = vtk.vtkPoints()
        self.pts.SetNumberOfPoints(4)
        
        self.lines = vtk.vtkCellArray()
        self.lines.InsertNextCell(5)
        for i in range(4):
            self.lines.InsertCellPoint(i)
        self.lines.InsertCellPoint(0)
        
        self.pd = vtk.vtkPolyData()
        self.pd.SetPoints(self.pts)
        self.pd.SetLines(self.lines)
        
        self.bboxMapper = vtk.vtkPolyDataMapper2D()
        self.bboxMapper.SetInput(self.pd)
        self.bboxActor = vtk.vtkActor2D()
        self.bboxActor.SetMapper(self.bboxMapper)
        self.bboxActor.GetProperty().SetColor(1, 0, 0)
        
        self.parent.renderer.AddViewProp(self.bboxActor)
        
        self.pts.SetPoint(0, self.X1, self.Y1, 0)
        self.pts.SetPoint(1, self.X2, self.Y1, 0)
        self.pts.SetPoint(2, self.X2, self.Y2, 0)
        self.pts.SetPoint(3, self.X1, self.Y2, 0)
        self.bboxEnabled = False
            
    def disable(self):
        self.bboxActor.VisibilityOff()
        #self.X1 = self.Y1 = self.X2 = self.Y2 = 0
    
    def getAllPoint(self):
        result = npy.empty([4, 3])
        space = self.parent.space
        if len(space) == 2:
            space += [1]
        for i in range(4):
            point = self.pts.GetPoint(i)
            self.parent.window_interactor.GetPicker().Pick(point[0], point[1], point[2], self.parent.window_interactor.GetRenderWindow().GetRenderers().GetFirstRenderer())
            picker = self.parent.window_interactor.GetPicker().GetPickPosition()
            result[i, :] = picker
        result = result / space
        return result
    def MouseMoveCallback(self, obj, event):
        if self.bboxEnabled:
            pos = self.parent.window_interactor.GetEventPosition()
            self.X2, self.Y2 = pos
        
            self.pts.SetPoint(1, self.X2, self.Y1, 0)
            self.pts.SetPoint(2, self.X2, self.Y2, 0)
            self.pts.SetPoint(3, self.X1, self.Y2, 0)
            
            self.parent.render_window.Render()
    def LeftButtonReleaseCallback(self, obj, event):
        pos = self.parent.window_interactor.GetEventPosition()
        self.X2, self.Y2 = pos
        self.bboxEnabled = False
        self.parent.render_window.Render()
        return True
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            if (self.X1, self.Y1) == (self.X2, self.Y2):
                return
                
            point = npy.round(self.getAllPoint())
            if self.parent.dimension:
                max = npy.max(point, axis = 0)
                min = npy.min(point, axis = 0)
                bound = [(min[i], max[i] + 1) for i in range(2)]
                bound = bound[::-1]
            else:
                point[0, self.parent.view] = 0
                point[1, self.parent.view] = self.parent.parent.getData().getData().shape[0] - 1
                max = npy.max(point, axis = 0)
                min = npy.min(point, axis = 0)
                bound = [(min[i], max[i] + 1) for i in range(3)]
                bound = bound[::-1]
            
            info = db.ImageInfo(self.parent.parent.getData().getInfo().data)
            info.setName(None)
            if not self.parent.dimension:
                orientation = npy.array([1, 0, 0, 0, 1, 0])
                info.addData('orientation', orientation)
                resolution = self.parent.parent.getData().getResolution()[::-1]
                info.addData('resolution', resolution)
                view, flip = db.getViewAndFlipFromOrientation(orientation, resolution.shape[0])
                info.addData('view', view)
                info.addData('flip', flip)
                info.addData('clip', npy.array([bound[0][0], bound[0][1], bound[1][0], 
                    bound[1][1], bound[2][0], bound[2][1]]))
                data = db.BasicData(data = self.parent.parent.getData().getData()[bound[0][0]:bound[0][1], 
                    bound[1][0]:bound[1][1], bound[2][0]:bound[2][1]], info = info)
            else:
                info.addData('clip', npy.array([bound[0][0], bound[0][1], bound[1][0], bound[1][1]]))
                data = db.BasicData(data = self.parent.parent.getData().getData()[bound[0][0]:bound[0][1], 
                    bound[1][0]:bound[1][1]], info = info)
                
            self.parent.parent.gui.addNewDataView(data)
        
    def LeftButtonPressCallback(self, obj, event):
        pos = self.parent.window_interactor.GetEventPosition()
        self.X1, self.Y1 = pos
        
        self.pts.SetPoint(0, self.X1, self.Y1, 0)
        self.pts.SetPoint(1, self.X1, self.Y1, 0)
        self.pts.SetPoint(2, self.X1, self.Y1, 0)
        self.pts.SetPoint(3, self.X1, self.Y1, 0)

        self.bboxEnabled = True
        self.bboxActor.VisibilityOn()
        
        return True
    def getName(self):
        return "Clip Tool"
