# -*- coding: utf-8 -*-
"""
Created on 2014-06-07

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Analysis.ContourErrorAnalysis import ContourErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_segmentation import ac_segmentation
import numpy as npy
import xlwt
import os, sys

class TestAllSegmentation(MacroBase):
    def getName(self):
        return 'Test All Segmentation'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test2.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.icp = IcpPointsetRegistration(None)
        self.contourerror = ContourErrorAnalysis(None)
        self.areaerror = AreaIndexAnalysis(None)
        
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        title = ['CCA', 'ECA', 'ICA', 'Overall']
        
        self.sheet1 = self.book.add_sheet('segmentation')
        self.sheet1.write(1, 0, 'MRE')
        
        for i in range(4):
            self.sheet1.write(i + 1, 1, title[i])
        
        self.sheet2 = self.book.add_sheet('registration')
        self.sheet2.write(1, 0, 'MRE')
        self.sheet2.write(5, 0, 'MAXE')
        self.sheet2.write(9, 0, 'Dice Index')
        
        for j in range(3):
            for i in range(4):
                self.sheet2.write(j * 4 + i + 1, 1, title[i])
        
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
        print 'Segment Data %s...' % self.ini.file.name_result[i]
        tmp = dataset['fix'].pointSet.data['Centerline']
        tmp = tmp[tmp[:, 0] >= 0]
        
        new_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        '''
        ind = npy.argsort(tmp[:, 2])
        tmp = tmp[ind]
        for cnt in range(1, 3):
            points = tmp[tmp[:, -1] == cnt]
            ind = npy.argmax(points[:, 2])
            zmin = npy.min(points[:, 2])
            center = points[ind, :]
            for z in ran
        '''
        j = 0
        for center in tmp:
            image = dataset['fix'].getData()[npy.round(center[2]), :, :].transpose().copy()
            image = (image - npy.min(image)) / (npy.max(image) - npy.min(image)) * 255
            result = ac_segmentation(center[:2], image)
            
            point_array = npy.insert(result.transpose(), 2, [[center[2]],[center[3]]], axis = 1)
            new_points = npy.append(new_points, point_array, 0)
            
            j += 1
            if j % 10 == 0:
                sys.stdout.write(str(j) + ',')
                sys.stdout.flush()
        print ' '
        print 'Done!'
        pointset = {'Contour': new_points}
        pointset['Centerline'] = calCenterlineFromContour(pointset)
        print 'Saving Data %s...' % self.ini.file.name_result[i]
        new_data = db.BasicData(dataset['fix'].data, db.ImageInfo(dataset['fix'].info.data), pointset)
        db.saveMatData(self.savepath + self.ini.file.name_result[i] + '_mr.mat', [new_data], 0)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.contourerror.analysis(new_data, dataset['fix'].getPointSet('Contour').copy())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        self.sheet1.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet1.write(j + 1, i + 2, mean_dis[j])
        self.sheet1.write(4, i + 2, mean_whole)
        
        self.book.save(self.path + self.ini.file.savedir + 'Test_segmentation.xls')
        
        
        # ICP with centerline
        print 'Register Data %s with ICP(centerline)...' % self.ini.file.name_result[i]
        data, point, para = self.icp.register(new_data, dataset['mov'], 1) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        mean_dis, mean_whole, max_dis, max_whole = self.contourerror.analysis(resultData, dataset['fix'].getPointSet('Contour').copy())
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
        
        self.book.save(self.path + self.ini.file.savedir + 'Test_segmentation.xls')
        del data, point, resultData
