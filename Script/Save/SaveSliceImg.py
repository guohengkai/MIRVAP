# -*- coding: utf-8 -*-
"""
Created on 2014-04-07

@author: Hengkai Guo
"""

from MIRVAP.Script.SaveBase import SaveBase
from MIRVAP.GUI.qvtk.WidgetView.ResultImageView import ResultImageView
import cv2

class SaveSliceImg(SaveBase):
    def getName(self):
        return 'Save current slice image'
    def save(self, window, data):
        name, ok = self.gui.getInputName(window)
        if ok and name:
            name = str(name)
            dir = './Data/%s.jpg' % name
            imgData = data.getData()
            
            if type(window.widgetView) is ResultImageView:
                status = window.widgetView.getDirectionAndSlice()
                slice = int(status[1] - 0.5)
                if window.widgetView.view == 2:
                    img = imgData[slice, :, :]
                elif window.widgetView.view == 1:
                    img = imgData[:, slice, :]
                elif window.widgetView.view == 0:
                    img = imgData[:, :, slice]
                else:
                    return False
                
                cv2.imwrite(dir, img)
                return True
                
            return False
