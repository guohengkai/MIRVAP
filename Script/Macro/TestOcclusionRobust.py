# -*- coding: utf-8 -*-
"""
Created on 2014-06-01

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys
import numpy as npy

class TestOcclusionRobust(MacroBase):
    def getName(self):
        return 'Test Occlusion Robustness'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.icp = IcpPointsetRegistration(None)
        self.contourerror = ContourErrorAnalysis(None)
        
        self.error = npy.zeros([7, 4], dtype = npy.float32)
        
        for i in range(self.cnt):
            dataset = self.load(i)
            self.process(dataset, i)
            del dataset
            
        self.error /= self.cnt
        
        self.book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        self.sheet = self.book.add_sheet('Occlusion Slice')
        
        for i in range(4):
            self.sheet.write(i + 1, 0, title[i])
        for i in range(7):
            self.sheet.write(0, i + 1, i + 1)
        for i in range(4):
            for j in range(7):
                self.sheet.write(i + 1, j + 1, float(self.error[j, i]))
        self.book.save('./Result/Robust_Occlusion.xls')
        
        if self.gui:
            self.gui.showErrorMessage('Success', 'Test sucessfully!')
        else:
            print 'Test sucessfully!'
            
    def load(self, i):
        dataset = {'mov': [], 'fix': []}
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir
            + self.ini.file.name_fix[i] + '.mat', None)
        point['Centerline'] = calCenterlineFromContour(point)
        fileData = db.BasicData(data, info, point)
        dataset['fix'] = fileData
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir
            + self.ini.file.name_mov[i] + '.mat', None)
        point['Centerline'] = calCenterlineFromContour(point)
        fileData = db.BasicData(data, info, point)
        dataset['mov'] = fileData
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
            
        return dataset
    def process(self, dataset, i):
        # ICP with centerline
        print 'Register Data %s with ICP(centerline)...' % self.ini.file.name_result[i]
        for fov in range(7):
            data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, False, 0, 9999.0, 1, fov + 1) 
            resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
            resultData.info.addData('fix', 1)
            resultData.info.addData('move', 2)
            resultData.info.addData('transform', para)
            print 'FOV %dmm Done!' % (fov + 1)
            mean_dis, mean_whole, max_dis, max_whole = self.contourerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy())
            print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
            self.error[fov, :3] += mean_dis
            self.error[fov, 3] += mean_whole
            del data, point, resultData
