# -*- coding: utf-8 -*-
"""
Created on 2014-02-06

@author: Hengkai Guo
"""

from PyQt4 import QtCore, QtGui
from Ui_MdiChildLoad import Ui_MdiChildLoad
from Plugin.NullPlugin import NullPlugin
import MIRVAP.Core.DataBase as db
import itk
import vtk
import numpy as npy

class MdiChildBase(QtGui.QMainWindow):
    def __init__(self, gui):
        super(MdiChildBase, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gui = gui
        self.isShow = False
    def setQVTKWidget(self):
        raise NotImplementedError('Method "setQVTKWidget" Not Impletemented!')
    def show(self):
        super(MdiChildBase, self).show()
        self.isShow = True
        # In order to get the correct size of window, it can't be put in the __init__ function
        self.setQVTKWidget()
    def closeEvent(self, event):
        self.isShow = False

class MdiChildLoad(MdiChildBase, Ui_MdiChildLoad):
    def __init__(self, gui, index):
        super(MdiChildLoad, self).__init__(gui)
        self.setupUi(self)
        
        self.index = index
        self.setWindowTitle(self.getName())
        self.plugin = NullPlugin()
        self.pluginIndex = self.gui.win.nullIndex
#        print '************************************'
#        print 'init'
#        print 'index:', self.index
#        print self.getData().pointSet.data
#        print '************************************'

    def getName(self):
        name = self.getData().getName()
        if not name:
            name = 'Data %d' % self.index
        return name
    def getData(self):
        return self.gui.dataModel[self.index]
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
    def setQVTKWidget(self):
        data = self.getData()
        image_type = data.getITKImageType()
        self.image = data.getITKImage()
        self.space = data.getResolution().tolist()
        # Resolution: x(col), y(row), z(slice) 
        if len(self.space) == 3:
            self.space = [float(x) / self.space[-1] for x in self.space]
        self.image.SetSpacing(self.space)
        shapeList = data.getData().shape
        y, x = shapeList[-2], shapeList[-1]
        self.dimension = len(shapeList) == 2
        
        itk_vtk_converter = itk.ImageToVTKImageFilter[image_type].New()
        itk_vtk_converter.SetInput(self.image)
        image_resample = vtk.vtkImageResample()
        image_resample.SetInput(itk_vtk_converter.GetOutput())
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = self.qvtkWidget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        
        self.reslice_mapper = vtk.vtkImageResliceMapper()
        self.reslice_mapper.SetInput(image_resample.GetOutput())
        self.reslice_mapper.SliceFacesCameraOn()
        self.reslice_mapper.SliceAtFocalPointOn()
        self.reslice_mapper.JumpToNearestSliceOn()
        self.reslice_mapper.BorderOff()
        self.reslice_mapper.BackgroundOn()
        
        array = data.getData()
        minI = array.min()
        maxI = array.max()
        image_property = vtk.vtkImageProperty()
        image_property.SetColorWindow(maxI - minI)
        image_property.SetColorLevel((maxI + minI) / 2.0)
        image_property.SetAmbient(0.0)
        image_property.SetDiffuse(1.0)
        image_property.SetOpacity(1.0)
        image_property.SetInterpolationTypeToLinear()
        
        image_slice = vtk.vtkImageSlice()
        image_slice.SetMapper(self.reslice_mapper)
        image_slice.SetProperty(image_property)
        
        self.renderer.AddViewProp(image_slice)
        
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
        if self.plugin.MouseMoveCallback(obj, event):
            return
        self.interactor_style.OnMouseMove()
    def LeftButtonReleaseCallback(self, obj, event):
        if self.plugin.LeftButtonReleaseCallback(obj, event):
            return
        self.interactor_style.OnLeftButtonUp()
        
    def KeyPressCallback(self, obj, event):
        if self.plugin.KeyPressCallback(obj, event):
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
        if self.plugin.LeftButtonPressCallback(obj, event):
            return
        self.window_interactor.SetAltKey(0)
        self.window_interactor.SetControlKey(0)
        self.window_interactor.SetShiftKey(0)
        self.interactor_style.OnLeftButtonDown()
        
    def MiddleButtonPressCallback(self, obj, event):
        if self.plugin.MiddleButtonPressCallback(obj, event):
            return
        self.window_interactor.SetAltKey(0)
        self.window_interactor.SetControlKey(0)
        self.window_interactor.SetShiftKey(0)
        self.interactor_style.OnMiddleButtonDown()
        
    def RightButtonPressCallback(self, obj, event):
        if self.plugin.RightButtonPressCallback(obj, event):
            return
        if self.dimension:
            return
        self.updateBefore()
        self.window_interactor.SetAltKey(0)
        self.window_interactor.SetControlKey(1)
        self.window_interactor.SetShiftKey(0)
        self.interactor_style.OnRightButtonDown()
    def RightButtonReleaseCallback(self, obj, event):
        if self.plugin.RightButtonReleaseCallback(obj, event):
            return
        self.interactor_style.OnRightButtonUp()
        self.updateAfter()
    def updateAfter(self, *arg):
        status = self.getDirectionAndSlice()
        self.gui.showMessageOnStatusBar("View: %s   Slice: %d" % status)
        self.plugin.updateAfter(self.view, int(status[1]), *arg)
    def updateBefore(self, *arg):
        status = self.getDirectionAndSlice()
        self.plugin.updateBefore(self.view, int(status[1]), *arg)
    def setPlugin(self, plugin, index):
        #print self.plugin
        #print plugin
        #print '----------------------'
#        if self.plugin == plugin:
#            return
        self.plugin.disable()
        self.plugin = plugin
        plugin.enable(self)
        self.pluginIndex = index
        self.render_window.Render()
        
        self.updateAfter()
        
    def getDirectionAndSlice(self):
        if self.dimension:
            return ('2D   ', 1)
        origin = self.reslice_mapper.GetSlicePlane().GetOrigin()
        #print camera.GetFocalPoint()
        if self.view == 0:
            return ('Sagittal', origin[0] / self.space[0] + 1)
        elif self.view == 1:
            return ('Coronal ', origin[1] / self.space[1] + 1)
        elif self.view == 2:
            return ('Axial   ', origin[2] / self.space[2] + 1)
    
    def save(self):
        self.plugin.save()
                
    def closeEvent(self, event):
        super(MdiChildLoad, self).closeEvent(event)
        self.save()
        name, ok = QtGui.QInputDialog.getText(self, "Save the data", 
            "Name:", QtGui.QLineEdit.Normal, self.getName())
        if ok and name:
            self.gui.showMessageOnStatusBar("Saving...")
            name = str(name)
            self.getData().setName(name)
            dir = './Data/' + name
            db.saveMatData(dir, self.getData())
        del self.image
        self.gui.dataModel.remove(self.index)
        self.gui.showMessageOnStatusBar("")
        import gc
        gc.collect()
        event.accept()
