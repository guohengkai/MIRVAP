# -*- coding: utf-8 -*-
"""
Created on 2014-04-26

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys
import time

class TestAllRegistration(MacroBase):
    def getName(self):
        return 'Test All Registration'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.icp = IcpPointsetRegistration(None)
        self.areaerror = AreaIndexAnalysis(None)
        self.surfaceerror = SurfaceErrorAnalysis(None)
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        
        self.sheet1 = self.book.add_sheet('icp_con')
        self.sheet1.write(1, 0, 'SRE')
        self.sheet1.write(5, 0, 'SMAXE')
        self.sheet1.write(9, 0, 'Dice Index')
        self.sheet1.write(13, 0, 'time')
        for j in range(3):
            for i in range(4):
                self.sheet1.write(j * 4 + i + 1, 1, title[i])
        
        self.sheet2 = self.book.add_sheet('icp_cen')
        self.sheet2.write(1, 0, 'SRE')
        self.sheet2.write(5, 0, 'SMAXE')
        self.sheet2.write(9, 0, 'Dice Index')
        self.sheet2.write(13, 0, 'time')
        for j in range(3):
            for i in range(4):
                self.sheet2.write(j * 4 + i + 1, 1, title[i])
                
        self.sheet3 = self.book.add_sheet('icp_con_label')
        self.sheet3.write(1, 0, 'SRE')
        self.sheet3.write(5, 0, 'SMAXE')
        self.sheet3.write(9, 0, 'Dice Index')
        self.sheet3.write(13, 0, 'time')
        for j in range(3):
            for i in range(4):
                self.sheet3.write(j * 4 + i + 1, 1, title[i])
        
        self.sheet4 = self.book.add_sheet('icp_cen_label')
        self.sheet4.write(1, 0, 'SRE')
        self.sheet4.write(5, 0, 'SMAXE')
        self.sheet4.write(9, 0, 'Dice Index')
        self.sheet4.write(13, 0, 'time')
        for j in range(3):
            for i in range(4):
                self.sheet4.write(j * 4 + i + 1, 1, title[i])
        
        for i in range(self.cnt):
            dataset = self.load(i)
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
        # ICP with contour without label
        print 'Register Data %s with ICP(contour) without label...' % self.ini.file.name_result[i]
        data, point, para, time = self.icp.register(dataset['fix'], dataset['mov'], 0, op = False, isTime = True) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        dice_index, dice_index_all = self.areaerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy())
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet1.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet1.write(j + 1, i + 2, mean_dis[j])
            self.sheet1.write(j + 5, i + 2, max_dis[j])
            self.sheet1.write(j + 9, i + 2, dice_index[j])
        self.sheet1.write(4, i + 2, mean_whole)
        self.sheet1.write(8, i + 2, max_whole)
        self.sheet1.write(12, i + 2, dice_index_all)
        self.sheet1.write(13, i + 2, time)
        self.book.save(self.path + self.ini.file.savedir + 'multimodal_feature.xls')
        del data, point, resultData
        
        # ICP with centerline without label
        print 'Register Data %s with ICP(centerline) without label...' % self.ini.file.name_result[i]
        data, point, para, time = self.icp.register(dataset['fix'], dataset['mov'], 1, op = True, isTime = True) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        dice_index, dice_index_all = self.areaerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy())
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet2.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet2.write(j + 1, i + 2, mean_dis[j])
            self.sheet2.write(j + 5, i + 2, max_dis[j])
            self.sheet2.write(j + 9, i + 2, dice_index[j])
        self.sheet2.write(4, i + 2, mean_whole)
        self.sheet2.write(8, i + 2, max_whole)
        self.sheet2.write(12, i + 2, dice_index_all)
        self.sheet2.write(13, i + 2, time)
        self.book.save(self.path + self.ini.file.savedir + 'multimodal_feature.xls')
        del data, point, resultData
        
        # ICP with contour with label
        print 'Register Data %s with ICP(contour) with label...' % self.ini.file.name_result[i]
        data, point, para, time = self.icp.register(dataset['fix'], dataset['mov'], 0, op = True, isTime = True) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        dice_index, dice_index_all = self.areaerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy())
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet3.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet3.write(j + 1, i + 2, mean_dis[j])
            self.sheet3.write(j + 5, i + 2, max_dis[j])
            self.sheet3.write(j + 9, i + 2, dice_index[j])
        self.sheet3.write(4, i + 2, mean_whole)
        self.sheet3.write(8, i + 2, max_whole)
        self.sheet3.write(12, i + 2, dice_index_all)
        self.sheet3.write(13, i + 2, time)
        self.book.save(self.path + self.ini.file.savedir + 'multimodal_feature.xls')
        del data, point, resultData
        
        # ICP with centerline with label
        print 'Register Data %s with ICP(centerline) with label...' % self.ini.file.name_result[i]
        data, point, para, time = self.icp.register(dataset['fix'], dataset['mov'], 1, op = False, isTime = True) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Contour').copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        dice_index, dice_index_all = self.areaerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy())
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet4.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet4.write(j + 1, i + 2, mean_dis[j])
            self.sheet4.write(j + 5, i + 2, max_dis[j])
            self.sheet4.write(j + 9, i + 2, dice_index[j])
        self.sheet4.write(4, i + 2, mean_whole)
        self.sheet4.write(8, i + 2, max_whole)
        self.sheet4.write(12, i + 2, dice_index_all)
        self.sheet4.write(13, i + 2, time)
        self.book.save(self.path + self.ini.file.savedir + 'multimodal_feature.xls')
        del data, point, resultData
         
if __name__ == "__main__":
    test = TestAllRegistration(None)
    test.run()
