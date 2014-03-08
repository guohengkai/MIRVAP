# -*- coding: utf-8 -*-
"""
Created on 2014-03-01

@author: Hengkai Guo
"""
from MIRVAP.GUI.Plugin.NullPlugin import NullPlugin
import itk, vtk
import numpy as npy

class WidgetViewBase(object):
    def __init__(self, parent):
        self.parent = parent
        self.type = 'any'
        self.datatype = (2, 3)
        if parent:
            self.plugin = [NullPlugin()]
            self.pluginIndex = self.parent.gui.win.nullIndex
    def setWidgetView(self, widget):
        self.parent.gui.showMessageOnStatusBar("Widget: " + self.getName())
    def getName(self):
        raise NotImplementedError('Method "getName" Not Impletemented!')
    def initView(self, data, widget):
        image_type = data.getITKImageType()
        self.image = data.getITKImage()
        self.space = data.getResolution().tolist()
        # Resolution: x(col), y(row), z(slice) 
        if len(self.space) == 3:
            self.space = [float(x) / self.space[-1] for x in self.space]
        #self.space = [1.0, 1.0, 1.0]
        self.image.SetSpacing(self.space)
        
        self.itk_vtk_converter = itk.ImageToVTKImageFilter[image_type].New()
        self.itk_vtk_converter.SetInput(self.image)
        self.image_resample = vtk.vtkImageResample()
        self.image_resample.SetInput(self.itk_vtk_converter.GetOutput())
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
    def save(self):
        pass
        
class SingleDataView(WidgetViewBase):
    '''
        Move left button:     Modify window level
        Move middle button:   Pan the camera
        Wheel middle button:  Zoom the camera
        Move right button:    Slice through the image
        
        Press R Key:          Reset the Window/Level
        Press X Key:          Reset to a sagittal view
        Press Y Key:          Reset to a coronal view
        Press Z Key:          Reset to an axial view
        Press Left/Right Key: Slice through the image
    '''
    def __init__(self, parent = None):
        super(SingleDataView, self).__init__(parent)
        self.type = 'load'
    def setWidgetView(self, widget):
        self.initView(self.parent.getData(), widget)
    def getName(self):
        return "Data View"
        
    def initView(self, data, widget):
        super(SingleDataView, self).initView(data, widget)
        
        shapeList = data.getData().shape
        y, x = shapeList[-2], shapeList[-1]
        self.dimension = len(shapeList) == 2
        
        self.reslice_mapper = vtk.vtkImageResliceMapper()
        self.reslice_mapper.SetInput(self.image_resample.GetOutput())
        self.reslice_mapper.SliceFacesCameraOn()
        self.reslice_mapper.SliceAtFocalPointOn()
        self.reslice_mapper.JumpToNearestSliceOn()
        self.reslice_mapper.BorderOff()
        self.reslice_mapper.BackgroundOn()
        
        array = data.getData()
        self.minI = array.min()
        self.maxI = array.max()
        image_property = vtk.vtkImageProperty()
        image_property.SetColorWindow(self.maxI - self.minI)
        image_property.SetColorLevel((self.maxI + self.minI) / 2.0)
        image_property.SetAmbient(0.0)
        image_property.SetDiffuse(1.0)
        image_property.SetOpacity(1.0)
        image_property.SetInterpolationTypeToLinear()
        
        self.image_slice = vtk.vtkImageSlice()
        self.image_slice.SetMapper(self.reslice_mapper)
        self.image_slice.SetProperty(image_property)
        
        self.renderer.AddViewProp(self.image_slice)
        
        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.interactor_style = vtk.vtkInteractorStyleImage()
        self.interactor_style.SetInteractionModeToImage3D()
        self.window_interactor.SetInteractorStyle(self.interactor_style)
        self.render_window.SetInteractor(self.window_interactor)
        point_picker = vtk.vtkPointPicker()
        self.window_interactor.SetPicker(point_picker)
        
        self.render_window.GlobalWarningDisplayOff()
        self.render_window.Render()
        self.camera = self.renderer.GetActiveCamera()
        self.camera.ParallelProjectionOn()
        w, h = self.window_interactor.GetSize()
        if h * x * self.space[0] < w * y * self.space[1]:
            scale = y / 2.0 * self.space[1]
        else:
            scale = h * x  * self.space[0] / 2.0 / w
        self.camera.SetParallelScale(scale)
        point = self.camera.GetFocalPoint()
        dis = self.camera.GetDistance()
        self.camera.SetViewUp(0, -1, 0)
        self.camera.SetPosition(point[0], point[1], point[2] - dis)
        self.renderer.ResetCameraClippingRange()
        
        # View of image
        self.view = 2
                
        self.interactor_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        self.interactor_style.AddObserver("LeftButtonReleaseEvent", self.LeftButtonReleaseCallback)
        self.interactor_style.AddObserver("LeftButtonPressEvent", self.LeftButtonPressCallback)
        self.interactor_style.AddObserver("MiddleButtonPressEvent", self.MiddleButtonPressCallback)
        self.interactor_style.AddObserver("RightButtonPressEvent", self.RightButtonPressCallback)
        self.interactor_style.AddObserver("RightButtonReleaseEvent", self.RightButtonReleaseCallback)
        self.interactor_style.AddObserver("KeyPressEvent", self.KeyPressCallback)
        self.interactor_style.AddObserver("CharEvent", self.CharCallback)
        
        self.updateAfter()
        
        self.render_window.Render()
    def MouseMoveCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.MouseMoveCallback(obj, event)
        if flag:
            return
        self.interactor_style.OnMouseMove()
    def LeftButtonReleaseCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.LeftButtonReleaseCallback(obj, event)
        if flag:
            return
        self.interactor_style.OnLeftButtonUp()
        
    def KeyPressCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.KeyPressCallback(obj, event)
        if flag:
            return
        ch = self.window_interactor.GetKeySym()
        if ch == 'r':
            self.interactor_style.OnChar()
            return            
        if self.dimension:
            return
        if ch in ['x', 'y', 'z']:
            self.updateBefore()
            # Flip the image along the axis y
            point = self.camera.GetFocalPoint()
            dis = self.camera.GetDistance()
            if ch == 'x':
                self.view = 0
                self.camera.SetViewUp(0, 0, 1)
                self.camera.SetPosition(point[0] + dis, point[1], point[2])
            elif ch == 'y':
                self.view = 1
                self.camera.SetViewUp(0, 0, 1)
                self.camera.SetPosition(point[0], point[1] - dis, point[2])
            elif ch == 'z':
                self.view = 2
                self.camera.SetViewUp(0, -1, 0)
                self.camera.SetPosition(point[0], point[1], point[2] - dis)
            self.render_window.Render()
            
            self.updateAfter()
            return
        if ch == 'Left' or ch == 'Right':
            self.updateBefore()
            
            delta = list(self.camera.GetDirectionOfProjection())
            pos = list(self.camera.GetPosition())
            point = list(self.camera.GetFocalPoint())
            if ch == 'Left':
                pos = [a - b for a, b in zip(pos, delta)]
                point = [a - b for a, b in zip(point, delta)]
                last = 1
            else:
                pos = [a + b for a, b in zip(pos, delta)]
                point = [a + b for a, b in zip(point, delta)]
                last = -1
            self.camera.SetPosition(pos)
            self.camera.SetFocalPoint(point)
            self.render_window.Render()
            
            self.updateAfter(last)
            return
        
    def CharCallback(self, obj, event):
        pass
    def LeftButtonPressCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.LeftButtonPressCallback(obj, event)
        if flag:
            return
        self.window_interactor.SetAltKey(0)
        self.window_interactor.SetControlKey(0)
        self.window_interactor.SetShiftKey(0)
        self.interactor_style.OnLeftButtonDown()
        
    def MiddleButtonPressCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.MiddleButtonPressCallback(obj, event)
        if flag:
            return
        self.window_interactor.SetAltKey(0)
        self.window_interactor.SetControlKey(0)
        self.window_interactor.SetShiftKey(0)
        self.interactor_style.OnMiddleButtonDown()
        
    def RightButtonPressCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.RightButtonPressCallback(obj, event)
        if flag or self.dimension:
            return
        self.updateBefore()
        self.window_interactor.SetAltKey(0)
        self.window_interactor.SetControlKey(1)
        self.window_interactor.SetShiftKey(0)
        self.interactor_style.OnRightButtonDown()
    def RightButtonReleaseCallback(self, obj, event):
        flag = False
        for plugin in self.plugin:
            flag = flag or plugin.RightButtonReleaseCallback(obj, event)
        if flag:
            return
        self.interactor_style.OnRightButtonUp()
        self.updateAfter()
    def updateAfter(self, *arg):
        status = self.getDirectionAndSlice()
        self.parent.gui.showMessageOnStatusBar("Widget: %s     View: %s    Slice: %d" % (self.getName(), status[0], status[1]))
        for plugin in self.plugin:
            plugin.updateAfter(self.view, int(status[1]), *arg)
    def updateBefore(self, *arg):
        status = self.getDirectionAndSlice()
        for plugin in self.plugin:
            plugin.updateBefore(self.view, int(status[1]), *arg)
        
    def setPlugin(self, plugin, index):
        if len(self.plugin) > 1:
            return
        self.plugin[0].disable()
        self.plugin[0] = plugin
        plugin.enable(self)
        self.pluginIndex = index
        self.render_window.Render()
        
        self.updateAfter()
        
    def getDirectionAndSlice(self):
        if self.dimension:
            return ('2D   ', 1)
        origin = self.reslice_mapper.GetSlicePlane().GetOrigin()
        if self.view == 0:
            return ('Sagittal', origin[0] / self.space[0] + 1)
        elif self.view == 1:
            return ('Coronal ', origin[1] / self.space[1] + 1)
        elif self.view == 2:
            return ('Axial   ', origin[2] / self.space[2] + 1)
    def save(self):
        for plugin in self.plugin:
            plugin.save()

class RegistrationDataView(SingleDataView):
    def __init__(self, parent = None):
        super(RegistrationDataView, self).__init__(parent)
        self.type = 'registration'
