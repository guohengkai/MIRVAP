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
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour, calCentroidFromContour
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_segmentation import ac_segmentation
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_function import ac_area
import numpy as npy
import xlwt
import os, sys
import time

class TestAllSegmentation(MacroBase):
    def getName(self):
        return 'Test All Segmentation'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
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
        self.sheet1.write(5, 0, 'Time')
        
        self.sheet2 = self.book.add_sheet('registration')
        self.sheet2.write(1, 0, 'MRE')
        self.sheet2.write(5, 0, 'MAXE')
        self.sheet2.write(9, 0, 'Dice Index')
        self.sheet2.write(13, 0, 'Time')
        
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
        def autoDetectContour(point, cnt, start, end, delta):
            self.new_points = npy.append(self.new_points, point, 0)
            points = point[:, :-2]
            count = 0
            for j in range(start + delta, end + delta, delta):
                center = calCentroidFromContour(points).reshape(2)
                image = dataset['fix'].getData()[j, :, :].transpose().copy()
                image = (image - npy.min(image)) / (npy.max(image) - npy.min(image)) * 255
                result = ac_segmentation(center, image)
                
                a1 = ac_area(points.transpose(), image.shape)
                a2 = ac_area(result, image.shape)
                rate = a2 * 1.0 / a1
                if rate >= min(1.5 + count * 0.2, 2.1) or rate <= 0.7:
                    temp_array = points.copy()
                    if cnt != 1 and rate > 0.7:
                        count += 1
                else:
                    temp_array = result.transpose().copy()
                    count = 0
                points = temp_array.copy()
                temp_array = npy.insert(temp_array, 2, [[j], [cnt]], 1)
                self.new_points = npy.append(self.new_points, temp_array, 0)
                
                sys.stdout.write(str(j) + ',')
                sys.stdout.flush()
            print ' '
        
        print 'Segment Data %s...' % self.ini.file.name_result[i]
        tmp = dataset['fix'].pointSet.data['Contour']
        tmp = tmp[tmp[:, 0] >= 0]
        
        self.new_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        time1 = time.time()
        bottom = int(npy.round(npy.min(tmp[:, 2])))
        bif = int(db.getBifurcation(tmp) + 0.5)
        up = int(npy.round(npy.max(tmp[:, 2])))
        
        point_vital = [0] * 3
        point_vital[0] = tmp[(npy.round(tmp[:, -1]) == 0) & (npy.round(tmp[:, 2]) == bottom)].copy()
        point_vital[1] = tmp[(npy.round(tmp[:, -1]) == 1) & (npy.round(tmp[:, 2]) == up)].copy()
        point_vital[2] = tmp[(npy.round(tmp[:, -1]) == 2) & (npy.round(tmp[:, 2]) == up)].copy()
            
        autoDetectContour(point_vital[0], 0, bottom, bif, 1)
        autoDetectContour(point_vital[1], 1, up, bif, -1)
        autoDetectContour(point_vital[2], 2, up, bif, -1)
        time2 = time.time()
        '''
        # Use centerline for contour
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
        '''        
        print ' '
        print 'Done! Time for segmentation is %0.2fs' % (time2 - time1)
        pointset = {'Contour': self.new_points}
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
        self.sheet1.write(5, i + 2, time2 - time1)
        
        self.book.save(self.path + self.ini.file.savedir + 'Test_segmentation_final_refined.xls')
        
        
        # ICP with centerline
        print 'Register Data %s with ICP(centerline)...' % self.ini.file.name_result[i]
        time1 = time.time()
        data, point, para = self.icp.register(new_data, dataset['mov'], 1) 
        time2 = time.time()
        print 'Done! Time for registration is %0.2fs' % (time2 - time1)
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
        self.sheet2.write(13, i + 2, time2 - time1)
        
        self.book.save(self.path + self.ini.file.savedir + 'Test_segmentation_final_refined.xls')
        del data, point, resultData
