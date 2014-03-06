# -*- coding: utf-8 -*-
"""
Created on 2014-03-06

@author: Hengkai Guo
"""

from MIRVAP.Core.WidgetViewBase import WidgetViewBase
import vtk

class MIPView(WidgetViewBase):
    def __init__(self, parent = None):
        super(MIPView, self).__init__(parent)
        self.type = 'any'
    def getName(self):
        return "MIP Image View"
    def setWidgetView(self, widget):
        self.initView(self.parent.getData(), widget)
        
        range = self.image_resample.GetOutput().GetScalarRange()
        
        # The scale need to be changed
        self.shifter = vtk.vtkImageShiftScale()
        self.shifter.SetShift(-1.0 * range[0])
        self.shifter.SetScale(255.0 / (range[1] - range[0]))
        self.shifter.SetOutputScalarTypeToUnsignedChar()
        self.shifter.SetInput(self.image_resample.GetOutput())
        self.shifter.ReleaseDataFlagOff()
        self.shifter.Update()
        
        mipfunction = vtk.vtkVolumeRayCastMIPFunction()
        mipfunction.SetMaximizeMethodToScalarValue()
        volume = vtk.vtkVolume()
        self.renderer.AddViewProp(volume)
        raycastMapper = vtk.vtkVolumeRayCastMapper()
        raycastMapper.SetInputConnection(self.shifter.GetOutputPort())
        volume.SetMapper(raycastMapper)
        raycastMapper.SetVolumeRayCastFunction(mipfunction)
        
        self.window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window.SetInteractor(self.window_interactor)
        
        self.render_window.Render()
        
        # Manually set to trackball style
        self.window_interactor.SetKeyCode('t')
        self.window_interactor.CharEvent()
        self.window_interactor.GetInteractorStyle().AddObserver("KeyPressEvent", self.KeyPressCallback)
        self.window_interactor.GetInteractorStyle().AddObserver("CharEvent", self.KeyPressCallback)
    def KeyPressCallback(self, obj, event):
        pass
            
