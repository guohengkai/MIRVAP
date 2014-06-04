# -*- coding: utf-8 -*-
"""
Created on 2014-06-03

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.Script.Analysis.ContourErrorWithAreaAnalysis import ContourErrorWithAreaAnalysis
from MIRVAP.Script.Analysis.WeightedContourErrorAnalysis import WeightedContourErrorAnalysis
from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.Script.Analysis.CenterlineErrorAnalysis import CenterlineErrorAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys

class TestNewContour(MacroBase):
    def getName(self):
        return 'Test New Contour Error'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.contourerror = ContourErrorAnalysis(None)
        self.contourareaerror = ContourErrorWithAreaAnalysis(None)
        self.contourweigherror = WeightedContourErrorAnalysis(None)
        self.surfaceerror = SurfaceErrorAnalysis(None)
        self.areaerror = AreaIndexAnalysis(None)
        self.centerlineerror = CenterlineErrorAnalysis(None)
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        
        self.sheet = self.book.add_sheet('icp_cen')
        self.sheet.write(1, 0, 'MRE')
        self.sheet.write(5, 0, 'MAXE')
        #self.sheet.write(9, 0, 'AWMRE')
        #self.sheet.write(9, 0, 'Dice Index')
        #self.sheet.write(13, 0, 'MCRE')
        #self.sheet.write(17, 0, 'MAXCRE')
        #for j in range(5):
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
        dataset = {'result': [], 'fix': [], 'mov': []}
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir
            + self.ini.file.name_result[i] + '_icp_cen.mat', None)
        dataset['result'] = db.BasicData(data, info, point)
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_fix[i] + '.mat', None)
        dataset['fix'] = db.BasicData(data, info, point)
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_mov[i] + '.mat', None)
        dataset['mov'] = db.BasicData(data, info, point)
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
        return dataset
    def process(self, dataset, i):
        print 'Evaluation Data %s...' % self.ini.file.name_result[i]
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getResolution().tolist())
        #mean_dis, mean_whole, max_dis, max_whole = self.contourareaerror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy())
        #mean_dis, mean_whole, max_dis, max_whole = self.contourweigherror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy())
        print 'Surface Error Done! Whole mean is %0.2fmm.' % mean_whole
        #mean_dis2, mean_whole2, max_dis2, max_whole2 = self.contourweigherror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy(), True)
        
        #dice_index, dice_index_all = self.areaerror.analysis(dataset['result'], dataset['fix'].getPointSet('Contour').copy())
        #print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        #cmean_dis, cmean_whole, cmax_dis, cmax_whole = self.centerlineerror.analysis(resultData, dataset['fix'].getPointSet('Centerline').copy())
        #print 'Centerline Error Done! Whole mean is %0.2fmm.' % cmean_whole
        
        self.sheet.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet.write(j + 1, i + 2, mean_dis[j])
            self.sheet.write(j + 5, i + 2, max_dis[j])
            #self.sheet.write(j + 9, i + 2, mean_dis2[j])
            #self.sheet.write(j + 9, i + 2, dice_index[j])
            #self.sheet.write(j + 13, i + 2, cmean_dis[j])
            #self.sheet.write(j + 17, i + 2, cmax_dis[j])
        self.sheet.write(4, i + 2, mean_whole)
        self.sheet.write(8, i + 2, max_whole)
        #self.sheet.write(12, i + 2, mean_whole2)
        #self.sheet.write(12, i + 2, dice_index_all)
        #self.sheet.write(16, i + 2, cmean_whole)
        #self.sheet.write(20, i + 2, cmax_whole)
        self.book.save(self.path + self.ini.file.savedir + 'SurfaceError.xls')
         
if __name__ == "__main__":
    test = TestAllRegistration(None)
    test.run()
