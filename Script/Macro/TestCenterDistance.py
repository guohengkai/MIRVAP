# -*- coding: utf-8 -*-
"""
Created on 2015-03-03

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

class TestCenterDistance(MacroBase):
    def getName(self):
        return 'Test Center Distance'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test_modal.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.icp = IcpPointsetRegistration(None)
        self.contourerror = ContourErrorAnalysis(None)
        self.surfaceerror = SurfaceErrorAnalysis(None)
        
        self.dis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.error = npy.zeros([len(self.dis), len(self.dis)], dtype = npy.float32)
        
        for i in range(self.cnt):
            dataset = self.load(i)
            self.process(dataset, i)
            del dataset
            
        self.error /= self.cnt
        
        self.book = xlwt.Workbook()
        self.sheet = self.book.add_sheet('Initial Slice')
        
        self.sheet.write(1, 0, 'mean')
        self.sheet.write(2, 0, 'std')
        
        for i in self.dis:
            self.sheet.write(0, i, i)
            self.sheet.write(i, 0, i)
        for i in self.dis:
            for j in self.dis:
                self.sheet.write(i + 1, j + 1, float(self.error[i, j]))
                    
        self.book.save('./Result/center_dis_merge.xls')
        
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
        for i in self.dis:
            for j in self.dis:
                data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, down_fix = i, down_mov = j) # CLICP
                #data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 0, False, delta) #SICP
                #data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, False, delta, op = True) #CICP
                #data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 0, False, delta, op = True) #SLICP
                resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
                resultData.info.addData('fix', 1)
                resultData.info.addData('move', 2)
                resultData.info.addData('transform', para)
                print 'Sample (%d, %d) Done!' % (i, j)
                mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
                print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
                self.error[i - 1, j - 1] += mean_whole
                del data, point, resultData
