# -*- coding: utf-8 -*-
"""
Created on 2014-03-11

@author: Hengkai Guo
"""

from MIRVAP.Script.LoadBase import LoadBase
import MIRVAP.Core.DataBase as db

import numpy as npy

class LoadPhantom(LoadBase):
    def __init__(self, gui):
        super(LoadPhantom, self).__init__(gui)
    def getName(self):
        return 'Load Registration Phantom'
    def run(self, *args, **kwargs):
        info_fix = self.getInfo()
        info_move = self.getInfo([2.0, 1.0, 3.0], 1)
        
        
    def getInfo(self, res = [1.0, 1.0, 1.0], ori = 0):
        info = db.ImageInfo()
        info.addData('modality', 'MR') 
        resolution = npy.array(res)
        info.addData('resolution', resolution)
        if ori == 0:
            orientation = npy.array([1, 0, 0, 0, 1, 0])
        elif ori == 1:
            orientation = npy.array([1, 0, 0, 0, 0, -1])
        elif ori == 2:
            orientation = npy.array([0, 1, 0, 0, 0, -1])
        info.addData('orientation', orientation)
        
        view, flip = db.getViewAndFlipFromOrientation(orientation, resolution.shape[0])
        info.addData('view', view)
        info.addData('flip', flip)
        
