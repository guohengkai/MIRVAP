# -*- coding: utf-8 -*-
"""
Created on 2014-04-07

@author: Hengkai Guo
"""

from MIRVAP.Script.SaveBase import SaveBase
from MIRVAP.GUI.qvtk.WidgetView.ResultImageView import ResultImageView
import numpy as npy
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
                    img = imgData[slice, :, :].copy()
                elif window.widgetView.view == 1:
                    img = imgData[:, slice, :].copy()
                elif window.widgetView.view == 0:
                    img = imgData[:, :, slice].copy()
                else:
                    return False
                
                img = (img - npy.min(img)) / (npy.max(img) - npy.min(img)) * 255
                cv2.imwrite(dir, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                return True
                
            return False
