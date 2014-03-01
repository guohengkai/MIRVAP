# -*- coding: utf-8 -*-
"""
Created on 2014-02-06

@author: Hengkai Guo
"""

from PyQt4 import QtCore, QtGui
from Ui_MdiChild import Ui_MdiChild
import MIRVAP.Core.DataBase as db
from MIRVAP.Core.WidgetViewBase import SingleDataView


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
    def getName(self):
        raise NotImplementedError('Method "getName" Not Impletemented!')
    def closeEvent(self, event):
        self.isShow = False

class MdiChildLoad(MdiChildBase, Ui_MdiChild):
    def __init__(self, gui, index):
        super(MdiChildLoad, self).__init__(gui)
        self.setupUi(self)
        
        self.index = index
        self.setWindowTitle(self.getName())
        
        self.widgetView = SingleDataView(self)

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
        self.widgetView.setWidgetView(self.qvtkWidget)

    
    def setPlugin(self, plugin, index):
        self.widgetView.setPlugin(plugin, index)
    
    def save(self):
        if self.isShow:
            self.widgetView.save()
                
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
        self.gui.dataModel.remove(self.index)
        self.gui.showMessageOnStatusBar("")
        import gc
        gc.collect()
        event.accept()
'''
class MdiChildRegistration(MdiChildBase, Ui_MdiChildRegistration):
    def __init__(self, gui, index):
        super(MdiChildRegistration, self).__init__(gui)
        self.setupUi(self)
        
        self.index = index
        self.fixedIndex = self.getData().getFixedIndex()
        self.movingIndex = self.getData().getMovingIndex()
        
        self.setWindowTitle(self.getName())
    def getData(self, index = -1):
        if index == -1:
            index = self.index
        return self.gui.dataModel[index]
    def setQVTKWidget(self):
        data = self.getData(self.movingIndex)
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
        self.render_window = self.oriQvtkWidget.GetRenderWindow()
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

    def getName(self):
        name = 'Data %d' % self.index
        return name
    def closeEvent(self, event):
        super(MdiChildRegistration, self).closeEvent(event)
        
        self.gui.dataModel.remove(self.index)
        self.gui.showMessageOnStatusBar("")
        
        event.accept()
'''
