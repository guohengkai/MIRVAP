# -*- coding: utf-8 -*-
"""
Created on 2014-04-26

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Registration.GmmregPointsetRegistration import GmmregPointsetRegistration
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.Script.Analysis.CenterlineErrorAnalysis import CenterlineErrorAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
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
            point['Centerline'] = calCenterlineFromContour(point)
            fileData = db.BasicData(data, info, point)
            dataset['fix'].append(fileData)
            
            data, info, point = db.loadMatData(self.path + self.ini.file.datadir
                + self.ini.file.name_mov[i] + '.mat', None)
            point['Centerline'] = calCenterlineFromContour(point)
            fileData = db.BasicData(data, info, point)
            dataset['mov'].append(fileData)
            print 'Data %s loaded!' % self.ini.file.name_result[i]
            
            
        return dataset
    def process(self, dataset):
        icp = IcpPointsetRegistration(None)
        gmm = GmmregPointsetRegistration(None)
        contourerror = ContourErrorAnalysis(None)
        areaerror = AreaIndexAnalysis(None)
        centerlineerror = CenterlineErrorAnalysis(None)
        savepath = self.path + self.ini.file.savedir
        book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        
        # ICP with contour
        sheet = book.add_sheet('icp_con')
        sheet.write(1, 0, 'MRE')
        sheet.write(5, 0, 'MAXE')
        sheet.write(9, 0, 'Dice Index')
        sheet.write(13, 0, 'MCRE')
        sheet.write(17, 0, 'MAXCRE')
        for j in range(5):
            for i in range(4):
                sheet.write(j * 4 + i + 1, 1, title[i])
        for i in range(self.cnt):
            print 'Register Data %s with ICP(contour)...' % self.ini.file.name_result[i]
            data, point, para = icp.register(dataset['fix'][i], dataset['mov'][i], 0) 
            resultData = db.BasicData(data, db.ImageInfo(dataset['fix'][i].info.data), point)
            print 'Saving Data %s...' % self.ini.file.name_result[i]
            db.saveMatData(savepath + self.ini.file.name_result[i] + '_icp_con.mat', [resultData], 0)
            print 'Done!'
            mean_dis, mean_whole, max_dis, max_whole = contourerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
            dice_index, dice_index_all = areaerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
            cmean_dis, cmean_whole, cmax_dis, cmax_whole = centerlineerror.analysis(resultData, dataset['fix'][i].getPointSet('Centerline').copy())
            print 'Centerline Error Done! Whole mean is %0.2fmm.' % cmean_whole
            
            sheet.write(0, i + 2, self.ini.file.name_result[i])
            for j in range(3):
                sheet.write(j + 1, i + 2, mean_dis[j])
                sheet.write(j + 5, i + 2, max_dis[j])
                sheet.write(j + 9, i + 2, dice_index[j])
                sheet.write(j + 13, i + 2, cmean_dis[j])
                sheet.write(j + 17, i + 2, cmax_dis[j])
            sheet.write(4, i + 2, mean_whole)
            sheet.write(8, i + 2, max_whole)
            sheet.write(12, i + 2, dice_index_all)
            sheet.write(16, i + 2, cmean_whole)
            sheet.write(20, i + 2, cmax_whole)
            book.save(self.path + self.ini.file.savedir + self.ini.file.name + '.xls')
            del data, point, resultData
        
        # ICP with centerline
        sheet = book.add_sheet('icp_cen')
        sheet.write(1, 0, 'MRE')
        sheet.write(5, 0, 'MAXE')
        sheet.write(9, 0, 'Dice Index')
        sheet.write(13, 0, 'MCRE')
        sheet.write(17, 0, 'MAXCRE')
        for j in range(5):
            for i in range(4):
                sheet.write(j * 4 + i + 1, 1, title[i])
        for i in range(self.cnt):
            print 'Register Data %s with ICP(centerline)...' % self.ini.file.name_result[i]
            data, point, para = icp.register(dataset['fix'][i], dataset['mov'][i], 1) 
            resultData = db.BasicData(data, db.ImageInfo(dataset['fix'][i].info.data), point)
            print 'Saving Data %s...' % self.ini.file.name_result[i]
            db.saveMatData(savepath + self.ini.file.name_result[i] + '_icp_cen.mat', [resultData], 0)
            print 'Done!'
            mean_dis, mean_whole, max_dis, max_whole = contourerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
            dice_index, dice_index_all = areaerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
            cmean_dis, cmean_whole, cmax_dis, cmax_whole = centerlineerror.analysis(resultData, dataset['fix'][i].getPointSet('Centerline').copy())
            print 'Centerline Error Done! Whole mean is %0.2fmm.' % cmean_whole
            
            sheet.write(0, i + 2, self.ini.file.name_result[i])
            for j in range(3):
                sheet.write(j + 1, i + 2, mean_dis[j])
                sheet.write(j + 5, i + 2, max_dis[j])
                sheet.write(j + 9, i + 2, dice_index[j])
                sheet.write(j + 13, i + 2, cmean_dis[j])
                sheet.write(j + 17, i + 2, cmax_dis[j])
            sheet.write(4, i + 2, mean_whole)
            sheet.write(8, i + 2, max_whole)
            sheet.write(12, i + 2, dice_index_all)
            sheet.write(16, i + 2, cmean_whole)
            sheet.write(20, i + 2, cmax_whole)
            book.save(self.path + self.ini.file.savedir + self.ini.file.name + '.xls')
            del data, point, resultData
            
        # GMM with contour
        sheet = book.add_sheet('gmm_con')
        sheet.write(1, 0, 'MRE')
        sheet.write(5, 0, 'MAXE')
        sheet.write(9, 0, 'Dice Index')
        sheet.write(13, 0, 'MCRE')
        sheet.write(17, 0, 'MAXCRE')
        for j in range(5):
            for i in range(4):
                sheet.write(j * 4 + i + 1, 1, title[i])
        for i in range(self.cnt):
            print 'Register Data %s with GMM(contour)...' % self.ini.file.name_result[i]
            data, point, para = gmm.register(dataset['fix'][i], dataset['mov'][i], 0) 
            resultData = db.BasicData(data, db.ImageInfo(dataset['fix'][i].info.data), point)
            print 'Saving Data %s...' % self.ini.file.name_result[i]
            db.saveMatData(savepath + self.ini.file.name_result[i] + '_gmm_con.mat', [resultData], 0)
            print 'Done!'
            mean_dis, mean_whole, max_dis, max_whole = contourerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
            dice_index, dice_index_all = areaerror.analysis(resultData, dataset['fix'][i].getPointSet('Contour').copy())
            print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
            cmean_dis, cmean_whole, cmax_dis, cmax_whole = centerlineerror.analysis(resultData, dataset['fix'][i].getPointSet('Centerline').copy())
            print 'Centerline Error Done! Whole mean is %0.2fmm.' % cmean_whole
            
            sheet.write(0, i + 2, self.ini.file.name_result[i])
            for j in range(3):
                sheet.write(j + 1, i + 2, mean_dis[j])
                sheet.write(j + 5, i + 2, max_dis[j])
                sheet.write(j + 9, i + 2, dice_index[j])
                sheet.write(j + 13, i + 2, cmean_dis[j])
                sheet.write(j + 17, i + 2, cmax_dis[j])
            sheet.write(4, i + 2, mean_whole)
            sheet.write(8, i + 2, max_whole)
            sheet.write(12, i + 2, dice_index_all)
            sheet.write(16, i + 2, cmean_whole)
            sheet.write(20, i + 2, cmax_whole)
            book.save(self.path + self.ini.file.savedir + self.ini.file.name + '.xls')
            del data, point, resultData
            
        del dataset
         
if __name__ == "__main__":
    test = TestAllRegistration(None)
    test.run()
