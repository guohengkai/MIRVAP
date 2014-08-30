# -*- coding: utf-8 -*-
"""
Created on 2014-08-30

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.NonrigidHybridRegistration import NonrigidHybridRegistration
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour, calCentroidFromContour
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_segmentation import ac_segmentation
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_function import ac_area

import xlwt
import os, sys, time
import numpy as npy

class TestNonrigidSegRegistration(MacroBase):
    def getName(self):
        return 'Test Non-rigid Registration with Segmentation'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.regPara = [(-1, -1, 'SSD'), (4.0, -1, 'SSD'), (-1, 1000, 'MI'), (32.0, 1000, 'MI'), 
            (-1, -1, 'MI'), (32.0, -1, 'MI'), (-1, 0, 'MI'), (32.0, 0, 'MI')]
        
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        
        self.sheet1 = self.book.add_sheet('MSD')
        for i in range(len(self.regPara)):
            self.sheet1.write(i + 1, 1, "type = %s beta = %fmm, w1 = %f" % (self.regPara[i][2], self.regPara[i][0], self.regPara[i][1]))
        
        self.sheet2 = self.book.add_sheet('DSC')
        for i in range(len(self.regPara)):
            self.sheet2.write(i + 1, 1, "type = %s beta = %fmm, w1 = %f" % (self.regPara[i][2], self.regPara[i][0], self.regPara[i][1]))
        
        self.sheet3 = self.book.add_sheet('Time')
        for i in range(len(self.regPara)):
            self.sheet3.write(i + 1, 1, "type = %s beta = %fmm, w1 = %f" % (self.regPara[i][2], self.regPara[i][0], self.regPara[i][1]))
            
        first = 0 # Add it by two each time when it crashes until it reach 20
        for i in range(first, self.cnt): 
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
        fileData = db.BasicData(data, info, point)
        dataset['fix'] = fileData
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir + '/Contour/'
            + self.ini.file.name_mov[i] + '.mat', None)
        fileData = db.BasicData(data, info, point)
        dataset['mov'] = fileData
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
        return dataset
    def process(self, dataset, i):
        def autoDetectContour(point, cnt, start, end, delta, res):
            self.new_points = npy.append(self.new_points, point, 0)
            points = point[:, :-2]
            d = 20
            count = 0
            for i in range(start + delta, end + delta, delta):
                center = calCentroidFromContour(points).reshape(2)
                image = dataset['fix'].getData()[i, :, :].transpose().copy()
                image = (image - npy.min(image)) / (npy.max(image) - npy.min(image)) * 255
                down = npy.max([npy.ceil(center[0] - d / res[0]), 0])
                up = npy.min([npy.floor(center[0] + d / res[0]), image.shape[0]])
                left = npy.max([npy.ceil(center[1] - d / res[1]), 0])
                right = npy.min([npy.floor(center[1] + d / res[1]), image.shape[1]])
                crop_image = image[down : up, left : right]
                center -= [down, left]
                
                result = ac_segmentation(center, crop_image)
                
                a1 = ac_area(points.transpose(), image.shape)
                a2 = ac_area(result, crop_image.shape)
                rate = a2 * 1.0 / a1
                if rate >= min(1.5 + count * 0.2, 2.1) or rate <= 0.7:
                    temp_array = points.copy()
                    if cnt != 1 and rate > 0.7:
                        count += 1
                else:
                    temp_array = result.transpose().copy()
                    temp_array[:, :2] += [down, left]
                    count = 0
                points = temp_array.copy()
                
                
                temp_array = npy.insert(temp_array, 2, [[i], [cnt]], 1)
                self.new_points = npy.append(self.new_points, temp_array, 0)
                
                sys.stdout.write(str(i) + ',')
                sys.stdout.flush()
            print ' '
            
        # Segmentation of data
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
            
        autoDetectContour(point_vital[0], 0, bottom, bif, 1, dataset['fix'].getResolution().tolist())
        autoDetectContour(point_vital[1], 1, up, bif, -1, dataset['fix'].getResolution().tolist())
        autoDetectContour(point_vital[2], 2, up, bif, -1, dataset['fix'].getResolution().tolist())
        print ' '
        print 'Finish segmentation of MR. '
        true_fixed_points = dataset['fix'].pointSet.data['Contour'].copy()
        dataset['fix'].pointSet.data['Contour'] = self.new_points
        dataset['fix'].pointSet.data['Centerline'] = calCenterlineFromContour(dataset['fix'].pointSet.data)
        
        hybrid = NonrigidHybridRegistration(None)
        print 'Register Data %s with Hybrid Method...' % (self.ini.file.name_result[i])
        data, point, para = hybrid.register(dataset['fix'], dataset['mov'], regPara = self.regPara, true_fixed_points = true_fixed_points)
        print 'Done!'
        
        for k in range(len(self.regPara)):
            self.sheet1.write(k + 1, i + 2, float(para[k, 0]))
            self.sheet2.write(k + 1, i + 2, float(para[k, 1]))
            self.sheet3.write(k + 1, i + 2, float(para[k, 2]))
        
        self.sheet1.write(0, i + 2, self.ini.file.name_result[i])
        self.sheet2.write(0, i + 2, self.ini.file.name_result[i])
        self.sheet3.write(0, i + 2, self.ini.file.name_result[i])
        self.book.save(self.path + self.ini.file.savedir + 'nonrigid' + str(first) + '.xls')
        del para
        del hybrid
        del true_fixed_points
