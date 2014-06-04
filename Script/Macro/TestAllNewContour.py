# -*- coding: utf-8 -*-
"""
Created on 2014-06-04

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.Script.Analysis.ContourErrorWithAreaAnalysis import ContourErrorWithAreaAnalysis
from MIRVAP.Script.Analysis.WeightedContourErrorAnalysis import WeightedContourErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.Script.Analysis.CenterlineErrorAnalysis import CenterlineErrorAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys

class TestAllNewContour(MacroBase):
    def getName(self):
        return 'Test All Contour Error Without Registration'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.contourerror = ContourErrorAnalysis(None)
        self.contourareaerror = ContourErrorWithAreaAnalysis(None)
        self.contourweigherror = WeightedContourErrorAnalysis(None)
        self.areaerror = AreaIndexAnalysis(None)
        self.centerlineerror = CenterlineErrorAnalysis(None)
        self.savepath = 'D:/ResultData/'
        self.dirs = ['icp-cen-clip-nolabel/', 'icp-cen-noclip-label/', 'icp-surface-clip-label/', 'icp-surface-noclip-nolabel/']
        self.type = ['_icp_cen.mat', '_icp_cen.mat', '_icp_con.mat', '_icp_con.mat']
        self.book = xlwt.Workbook()
        
        self.sheet = self.book.add_sheet('icp_cen')
        self.sheet.write(1, 0, 'MRE')
        self.sheet.write(2, 0, 'AMRE')
        self.sheet.write(3, 0, 'WMRE')
        self.sheet.write(4, 0, 'AWMRE')
        for k in range(4):
            for i in range(self.cnt):
                dataset = self.load(k, i)
                self.process(dataset, k, i)
                del dataset
        if self.gui:
            self.gui.showErrorMessage('Success', 'Test sucessfully!')
        else:
            print 'Test sucessfully!'
            
    def load(self, k, i):
        dataset = {'result': [], 'fix': []}
        data, info, point = db.loadMatData(self.savepath + self.dirs[k]
            + self.ini.file.name_result[i] + self.type[k], None)
        dataset['result'] = db.BasicData(data, info, point)
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_fix[i] + '.mat', None)
        dataset['fix'] = db.BasicData(data, info, point)
        
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
        return dataset
    def process(self, dataset, k, i):
        self.sheet.write(0, k * 20 + i + 1, self.ini.file.name_result[i] + str(k))
        print 'Evaluation Data %s...' % self.ini.file.name_result[i]
        mean_dis, mean_whole, max_dis, max_whole = self.contourerror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy())
        self.sheet.write(1, k * 20 + i + 1, mean_whole)
        mean_dis, mean_whole, max_dis, max_whole = self.contourareaerror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy())
        self.sheet.write(2, k * 20 + i + 1, mean_whole)
        mean_dis, mean_whole, max_dis, max_whole = self.contourweigherror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy())
        self.sheet.write(3, k * 20 + i + 1, mean_whole)
        mean_dis, mean_whole, max_dis, max_whole = self.contourweigherror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy(), True)
        self.sheet.write(4, k * 20 + i + 1, mean_whole)
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        
        self.book.save(self.path + self.ini.file.savedir + 'AllTest.xls')
         
if __name__ == "__main__":
    test = TestAllRegistration(None)
    test.run()
