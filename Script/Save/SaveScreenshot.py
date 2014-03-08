# -*- coding: utf-8 -*-
"""
Created on 2014-03-08

@author: Hengkai Guo
"""

from MIRVAP.Script.SaveBase import SaveBase
import vtk

class SaveScreenshot(SaveBase):
    def getName(self):
        return 'Save the screenshot'
    def save(self, window, data):
        name, ok = self.gui.getInputName(window)
        if ok and name:
            name = str(name)
            dir = './Data/%s.jpg' % name
            
            render_window = window.qvtkWidget.GetRenderWindow()
            window_image_filter = vtk.vtkWindowToImageFilter()
            writer = vtk.vtkJPEGWriter()
            window_image_filter.SetInput(render_window)
            window_image_filter.Update()
            
            writer.SetInputConnection(window_image_filter.GetOutputPort())
            writer.SetFileName(dir)
            render_window.Render()
            writer.Write()
            return True
