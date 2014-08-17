# -*- coding: utf-8 -*-
"""
Created on 2014-08-17

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis
import xlwt
import os, sys

class TestMaskRegistration(MacroBase):
    def getName(self):
        return 'Test Mask of Center Registration'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.icp = IcpPointsetRegistration(None)
        self.surfaceerror = SurfaceErrorAnalysis(None)
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        
        self.sheet = self.book.add_sheet('mask')
        self.sheet.write(1, 0, 'With mask')
        self.sheet.write(5, 0, 'Without mask')
        
        for j in range(2):
            for i in range(4):
                self.sheet.write(j * 4 + i + 1, 1, title[i])
        
        for i in range(self.cnt):
            dataset = self.load(i)
            self.sheet.write(0, i + 2, self.ini.file.name_result[i])
            self.process(dataset, i)
            del dataset
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
        print 'Register Data %s with mask...' % (self.ini.file.name_result[i])
        data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, useMask = True)
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), 
            dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        
        for j in range(3):
            self.sheet.write(j + 1, i + 2, mean_dis[j])
        self.sheet.write(4, i + 2, mean_whole)
        self.book.save(self.path + self.ini.file.savedir + 'mask.xls')
        del data, point, resultData
        
        print 'Register Data %s without mask...' % (self.ini.file.name_result[i])
        data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1)
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), 
            dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        
        for j in range(3):
            self.sheet.write(j + 5, i + 2, mean_dis[j])
        self.sheet.write(8, i + 2, mean_whole)
        self.book.save(self.path + self.ini.file.savedir + 'mask.xls')
        del data, point, resultData
