# -*- coding: utf-8 -*-
"""
Created on 2014-05-31

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys
import numpy as npy

class TestInitialRobust(MacroBase):
    def getName(self):
        return 'Test Initial Robustness'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test_modal.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.icp = IcpPointsetRegistration(None)
        self.contourerror = ContourErrorAnalysis(None)
        self.surfaceerror = SurfaceErrorAnalysis(None)
        
        self.error = npy.zeros([31, 2], dtype = npy.float32)
        
        for i in range(self.cnt):
            dataset = self.load(i)
            self.process(dataset, i)
            del dataset
            
        self.error[:, 0] /= self.cnt
        self.error[:, 1] = npy.sqrt((self.error[:, 1] - self.error[:, 0] ** 2 * self.cnt) / (self.cnt - 1))
        
        self.book = xlwt.Workbook()
        self.sheet = self.book.add_sheet('Initial Slice')
        
        self.sheet.write(1, 0, 'mean')
        self.sheet.write(2, 0, 'std')
        for i in range(-15, 16):
            self.sheet.write(0, i + 16, i)
        for i in range(2):
            for j in range(31):
                self.sheet.write(i + 1, j + 1, float(self.error[j, i]))
        self.book.save('./Result/Initial_merge.xls')
        
        if self.gui:
            self.gui.showErrorMessage('Success', 'Test sucessfully!')
        else:
            print 'Test sucessfully!'
            
    def load(self, i):
        dataset = {'mov': [], 'fix': []}
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_fix[i] + '.mat', None)
        point['Centerline'] = calCenterlineFromContour(point)
        fileData = db.BasicData(data, info, point)
        dataset['fix'] = fileData
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_mov[i] + '.mat', None)
        point['Centerline'] = calCenterlineFromContour(point)
        fileData = db.BasicData(data, info, point)
        dataset['mov'] = fileData
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
            
        return dataset
    def process(self, dataset, i):
        # ICP with centerline
        print 'Register Data %s with ICP(centerline)...' % self.ini.file.name_result[i]
        for delta in range(-15, 16):
            data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, False, delta) # CLICP
            #data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 0, False, delta) #SICP
            #data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, False, delta, op = True) #CICP
            #data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 0, False, delta, op = True) #SLICP
            resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
            resultData.info.addData('fix', 1)
            resultData.info.addData('move', 2)
            resultData.info.addData('transform', para)
            print 'Delta %dmm Done!' % delta
            mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
            print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
            self.error[delta + 15, 0] += mean_whole
            self.error[delta + 15, 1] += mean_whole ** 2
            del data, point, resultData

