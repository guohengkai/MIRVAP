# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.WidgetViewBase import RegistrationDataView
import itk, vtk
import numpy as npy

class ComparingImageView(RegistrationDataView):
    def setWidgetView(self, widget):
        self.initView(self.parent.getData('fix'), widget)
        
        data = self.parent.getData()
        image_type = data.getITKImageType()
        self.image2 = data.getITKImage()
        self.space2 = data.getResolution().tolist()
        
        if len(self.space2) == 3:
            self.space2 = [float(x) / self.space2[-1] for x in self.space2]
        self.image2.SetSpacing(self.space2)
        shapeList = data.getData().shape
        y, x = shapeList[-2], shapeList[-1]
        
        itk_vtk_converter = itk.ImageToVTKImageFilter[image_type].New()
        itk_vtk_converter.SetInput(self.image2)
        image_resample = vtk.vtkImageResample()
        image_resample.SetInput(itk_vtk_converter.GetOutput())
        
        self.renderer2 = vtk.vtkRenderer()
        self.render_window.AddRenderer(self.renderer2)
        
        self.reslice_mapper2 = vtk.vtkImageResliceMapper()
        self.reslice_mapper2.SetInput(image_resample.GetOutput())
        self.reslice_mapper2.SliceFacesCameraOn()
        self.reslice_mapper2.SliceAtFocalPointOn()
        self.reslice_mapper2.JumpToNearestSliceOn()
        self.reslice_mapper2.BorderOff()
        self.reslice_mapper2.BackgroundOn()
        
        array = data.getData()
        self.minI2 = array.min()
        self.maxI2 = array.max()
        self.image_slice2 = vtk.vtkImageSlice()
        self.image_slice2.SetMapper(self.reslice_mapper2)
        image_property2 = vtk.vtkImageProperty()
        image_property2.SetColorWindow(self.maxI2 - self.minI2)
        image_property2.SetColorLevel((self.maxI2 + self.minI2) / 2.0)
        image_property2.SetAmbient(0.0)
        image_property2.SetDiffuse(1.0)
        image_property2.SetOpacity(1.0)
        image_property2.SetInterpolationTypeToLinear()
        self.image_slice2.SetProperty(image_property2)
        
        self.renderer2.AddViewProp(self.image_slice2)
        
        self.renderer.SetViewport(0, 0, 0.5, 1)
        self.renderer2.SetViewport(0.5, 0, 1, 1)
        
        self.renderer2.SetActiveCamera(self.camera)
        self.render_window.Render()
        
    def getName(self):
        return "Comparing Image View"
    def KeyPressCallback(self, obj, event):
        ch = self.window_interactor.GetKeySym()
        if ch == 'r':
            image_property = self.image_slice.GetProperty()
            image_property.SetColorWindow(self.maxI - self.minI)
            image_property.SetColorLevel((self.maxI + self.minI) / 2.0)
            image_property2 = self.image_slice2.GetProperty()
            image_property2.SetColorWindow(self.maxI2 - self.minI2)
            image_property2.SetColorLevel((self.maxI2 + self.minI2) / 2.0)
            self.render_window.Render()
            return
        super(ComparingImageView, self).KeyPressCallback(obj, event)    
    def updateAfter(self, *arg):
        super(ComparingImageView, self).updateAfter(*arg)
        newMessage = "  (Left: Fixed image, Right: Result image)"
        self.parent.gui.showMessageOnStatusBar(self.parent.gui.getMessageOnStatusBar() + newMessage)
