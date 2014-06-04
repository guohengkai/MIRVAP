# -*- coding: utf-8 -*-
"""
Created on 2014-06-04

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys

class TestContourArea(MacroBase):
    def getName(self):
        return 'Test Contour Area'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.contourerror = ContourErrorAnalysis(None)
        self.areaerror = AreaIndexAnalysis(None)
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        
        self.sheet = self.book.add_sheet('icp_cen')
        self.sheet.write(1, 0, 'MR Area')
        self.sheet.write(5, 0, 'US Area')
        for j in range(2):
            for i in range(4):
                self.sheet.write(j * 4 + i + 1, 1, title[i])
        
        for i in range(self.cnt):
            dataset = self.load(i)
            self.process(dataset, i)
            del dataset
        if self.gui:
            self.gui.showErrorMessage('Success', 'Test sucessfully!')
        else:
            print 'Test sucessfully!'
            
    def load(self, i):
        dataset = {'result': [], 'fix': []}
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir
            + self.ini.file.name_result[i] + '_icp_cen.mat', None)
        dataset['result'] = db.BasicData(data, info, point)
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_fix[i] + '.mat', None)
        dataset['fix'] = db.BasicData(data, info, point)
        
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
        return dataset
    def process(self, dataset, i):
        print 'Evaluation Data %s...' % self.ini.file.name_result[i]
        dice_index, dice_index_all, mr_area, us_area = self.areaerror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy(), True)
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(4):
            self.sheet.write(j + 1, i + 2, mr_area[j])
            self.sheet.write(j + 5, i + 2, us_area[j])
        self.book.save(self.path + self.ini.file.savedir + 'Area.xls')
         
if __name__ == "__main__":
    test = TestAllRegistration(None)
    test.run()
