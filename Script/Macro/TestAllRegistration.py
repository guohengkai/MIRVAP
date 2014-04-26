# -*- coding: utf-8 -*-
"""
Created on 2014-04-26

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
import xlwt
import os, sys

class TestAllRegistration(MacroBase):
    def getName(self):
        return 'Test All Registration'
    def load(self):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        dataset = {'mov': [], 'fix': []}
        self.cnt = len(self.ini.file.name_fix)
        
        for i in range(self.cnt):
            data, info, point = db.loadMatData(self.path + self.ini.file.datadir
                + self.ini.file.name_fix[i] + '.mat', None)
            fileData = db.BasicData(data, info, point)
            dataset['fix'].append(fileData)
            
            data, info, point = db.loadMatData(self.path + self.ini.file.datadir
                + self.ini.file.name_mov[i] + '.mat', None)
            fileData = db.BasicData(data, info, point)
            dataset['mov'].append(fileData)
            print 'Data %s loaded!' % self.ini.file.name_result[i]
        return dataset
    def process(self, dataset):
        icp = IcpPointsetRegistration(None)
        contourerror = ContourErrorAnalysis(None)
        savepath = self.path + self.ini.file.savedir
        book = xlwt.Workbook()
        sheet = book.add_sheet('ContourError')
        for i in range(self.cnt):
            print 'Register Data %s...' % self.ini.file.name_result[i]
            data, point, para = icp.register(dataset['fix'][i], dataset['mov'][i], 0) 
            resultData = db.BasicData(data, db.ImageInfo(dataset['fix'][i].info.data), point)
            print 'Saving Data %s...' % self.ini.file.name_result[i]
            db.saveMatData(savepath + self.ini.file.name_result[i] + '_icp_con.mat', [resultData], 0)
            print 'Done!'
            mean_dis, mean_whole, max_dis, max_whole = contourerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Contour Error Done! Mean_whole is %0.2fmm.' % mean_whole
            
            for j in range(3):
                sheet.write(j, i, mean_dis[j])
                sheet.write(j + 4, i, max_dis[j])
            sheet.write(3, i, mean_whole)
            sheet.write(7, i, max_whole)
            
            del data, point, resultData
        del dataset
         
        book.save(self.path + self.ini.file.savedir + self.ini.file.name + '.xls')
