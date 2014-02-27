# -*- coding: utf-8 -*-
"""
Created on 2014-02-05

@author: Hengkai Guo
"""

from MIRVAP.Core.GuiBase import GuiBase

class TestGui(GuiBase):
    def __init__(self):
        super(TestGui, self).__init__()
        
    def getFileNames(self, *args):
        # For Test
        #dir = "E:/Python Programs/MIRVAP/Test/Data/MRI_37_3D_LEFT.mat"
        dir = ["E:\\Matlab Programs\\Register\\crop37\\left\\IM_1649"]
        #dir = ["E:\\Matlab Programs\\Register\\crop37\\brain+carotid\\DICOM\\IM_1111"]
        #dir = ['E:\\Matlab Programs\\test/IM_0453', 'E:\\Matlab Programs\\test/IM_0454', 'E:\\Matlab Programs\\test/IM_0455', 'E:\\Matlab Programs\\test/IM_0456']
        #dir = ['E:\\Matlab Programs\\test/IM_0011', 'E:\\Matlab Programs\\test/IM_0012', 'E:\\Matlab Programs\\test/IM_0013', 'E:\\Matlab Programs\\test/IM_0014', 'E:\\Matlab Programs\\test/IM_0015']
        return dir
    def startApplication(self):
        pass
