# -*- coding: utf-8 -*-
"""
Created on 2014-08-24

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.IcpPointsetRegistration import IcpPointsetRegistration
from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis
from MIRVAP.Script.Analysis.AreaIndexAnalysis import AreaIndexAnalysis
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour, calCentroidFromContour
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_segmentation import ac_segmentation
from MIRVAP.GUI.qvtk.Plugin.util.acontour.ac_function import ac_area
import xlwt
import os, sys
import time
import numpy as npy
import MIRVAP.Script.Registration.util.RegistrationUtil as util
import numpy.matlib as ml

class TestAllSegRegistration(MacroBase):
    def getName(self):
        return 'Test All Registration with Segmentation'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test_contrast.ini')
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
        for j in range(3):
            for i in range(4):
                self.sheet1.write(j * 4 + i + 1, 1, title[i])
        
        self.sheet2 = self.book.add_sheet('icp_cen')
        self.sheet2.write(1, 0, 'SRE')
        self.sheet2.write(5, 0, 'SMAXE')
        self.sheet2.write(9, 0, 'Dice Index')
        for j in range(3):
            for i in range(4):
                self.sheet2.write(j * 4 + i + 1, 1, title[i])
                
        self.sheet3 = self.book.add_sheet('icp_con_label')
        self.sheet3.write(1, 0, 'SRE')
        self.sheet3.write(5, 0, 'SMAXE')
        self.sheet3.write(9, 0, 'Dice Index')
        for j in range(3):
            for i in range(4):
                self.sheet3.write(j * 4 + i + 1, 1, title[i])
        
        self.sheet4 = self.book.add_sheet('icp_cen_label')
        self.sheet4.write(1, 0, 'SRE')
        self.sheet4.write(5, 0, 'SMAXE')
        self.sheet4.write(9, 0, 'Dice Index')
        for j in range(3):
            for i in range(4):
                self.sheet4.write(j * 4 + i + 1, 1, title[i])
        
        for i in range(0, 2):
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
        def autoDetectContour(point, cnt, start, end, delta, res, type):
            self.new_points = npy.append(self.new_points, point, 0)
            points = point[:, :-2]
            d = 20
            count = 0
            for i in range(start + delta, end + delta, delta):
                center = calCentroidFromContour(points).reshape(2)
                image = dataset[type].getData()[i, :, :].transpose().copy()
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
        bottom = int(npy.round(npy.min(tmp[:, 2])))
        bif = int(db.getBifurcation(tmp) + 0.5)
        up = int(npy.round(npy.max(tmp[:, 2])))
        bottom += (bif - bottom) / 2
        up -= (up - bif) / 2
        
        point_vital = [0] * 3
        point_vital[0] = tmp[(npy.round(tmp[:, -1]) == 0) & (npy.round(tmp[:, 2]) == bottom)].copy()
        point_vital[1] = tmp[(npy.round(tmp[:, -1]) == 1) & (npy.round(tmp[:, 2]) == up)].copy()
        point_vital[2] = tmp[(npy.round(tmp[:, -1]) == 2) & (npy.round(tmp[:, 2]) == up)].copy()
        
        autoDetectContour(point_vital[0], 0, bottom, bif, 1, dataset['fix'].getResolution().tolist(), 'fix')
        autoDetectContour(point_vital[1], 1, up, bif, -1, dataset['fix'].getResolution().tolist(), 'fix')
        autoDetectContour(point_vital[2], 2, up, bif, -1, dataset['fix'].getResolution().tolist(), 'fix')
        print ' '
        print 'Finish segmentation for fix data. '
        pointset = {'Contour': self.new_points}
        dataset['fix'].pointSet.data['Centerline'] = calCenterlineFromContour(pointset)
        self.new_points_fix = self.new_points.copy()
        # For mov data
        tmp = dataset['mov'].pointSet.data['Contour']
        tmp = tmp[tmp[:, 0] >= 0]
        
        self.new_points = npy.array([[-1, -1, -1, -1]], dtype = npy.float32)
        bottom = int(npy.round(npy.min(tmp[:, 2])))
        bif = int(db.getBifurcation(tmp) + 0.5)
        up = int(npy.round(npy.max(tmp[:, 2])))
        bottom += (bif - bottom) / 2
        up -= (up - bif) / 2
        
        point_vital = [0] * 3
        point_vital[0] = tmp[(npy.round(tmp[:, -1]) == 0) & (npy.round(tmp[:, 2]) == bottom)].copy()
        point_vital[1] = tmp[(npy.round(tmp[:, -1]) == 1) & (npy.round(tmp[:, 2]) == up)].copy()
        point_vital[2] = tmp[(npy.round(tmp[:, -1]) == 2) & (npy.round(tmp[:, 2]) == up)].copy()
            
        autoDetectContour(point_vital[0], 0, bottom, bif, 1, dataset['mov'].getResolution().tolist(), 'mov')
        autoDetectContour(point_vital[1], 1, up, bif, -1, dataset['mov'].getResolution().tolist(), 'mov')
        autoDetectContour(point_vital[2], 2, up, bif, -1, dataset['mov'].getResolution().tolist(), 'mov')
        print ' '
        print 'Finish segmentation for mov data. '
        pointset = {'Contour': self.new_points}
        dataset['mov'].pointSet.data['Centerline'] = calCenterlineFromContour(pointset)
        self.new_points_mov = self.new_points.copy()
        
        # ICP with centerline without label
        print 'Register Data %s with ICP(centerline) without label...' % self.ini.file.name_result[i]
        data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, op = True) 
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
        self.book.save(self.path + self.ini.file.savedir + 'multicontrast_seg_feature.xls')
        del data, point, resultData
        
        # ICP with centerline with label
        print 'Register Data %s with ICP(centerline) with label...' % self.ini.file.name_result[i]
        data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 1, op = False) 
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
        self.book.save(self.path + self.ini.file.savedir + 'multicontrast_seg_feature.xls')
        del data, point, resultData
        
        fix_points = dataset['fix'].getPointSet('Contour').copy()
        dataset['fix'].pointSet.data['Contour'] = self.new_points_fix
        mov_points = dataset['mov'].getPointSet('Contour').copy()
        dataset['mov'].pointSet.data['Contour'] = self.new_points_mov
        print 'Saving Data %s...' % self.ini.file.name_result[i]
        db.saveMatData(self.path + self.ini.file.savedir + self.ini.file.name_result[i] + '_snap.mat', [dataset['fix']], 0)
        db.saveMatData(self.path + self.ini.file.savedir + self.ini.file.name_result[i] + '_merge.mat', [dataset['mov']], 0)
        print 'Done!'
        
        # ICP with contour without label
        print 'Register Data %s with ICP(contour) without label...' % self.ini.file.name_result[i]
        data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 0, op = False) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, fix_points.copy(), mov_points.copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        para = resultData.info.getData('transform')
        R = ml.mat(para[:9]).reshape(3, 3)
        T = ml.mat(para[9:12]).T
        T = R.I * T
        T = -T
        tmp_con, result_center_points = util.resliceTheResultPoints(mov_points, None, 20, dataset['mov'].getResolution().tolist(), 
            dataset['fix'].getResolution().tolist(), False, R, T)
        resultData.pointSet.data['Contour'] = tmp_con
        dice_index, dice_index_all = self.areaerror.analysis(resultData, fix_points.copy())
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet1.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet1.write(j + 1, i + 2, mean_dis[j])
            self.sheet1.write(j + 5, i + 2, max_dis[j])
            self.sheet1.write(j + 9, i + 2, dice_index[j])
        self.sheet1.write(4, i + 2, mean_whole)
        self.sheet1.write(8, i + 2, max_whole)
        self.sheet1.write(12, i + 2, dice_index_all)
        self.book.save(self.path + self.ini.file.savedir + 'multicontrast_seg_feature.xls')
        del data, point, resultData
        
        # ICP with contour with label
        print 'Register Data %s with ICP(contour) with label...' % self.ini.file.name_result[i]
        data, point, para = self.icp.register(dataset['fix'], dataset['mov'], 0, op = True) 
        resultData = db.ResultData(data, db.ImageInfo(dataset['fix'].info.data), point)
        resultData.info.addData('fix', 1)
        resultData.info.addData('move', 2)
        resultData.info.addData('transform', para)
        print 'Done!'
        mean_dis, mean_whole, max_dis, max_whole = self.surfaceerror.analysis(resultData, fix_points.copy(), mov_points.copy(), dataset['mov'].getPointSet('Mask').copy(), dataset['mov'].getResolution().tolist())
        print 'Contour Error Done! Whole mean is %0.2fmm.' % mean_whole
        para = resultData.info.getData('transform')
        R = ml.mat(para[:9]).reshape(3, 3)
        T = ml.mat(para[9:12]).T
        T = R.I * T
        T = -T
        tmp_con, result_center_points = util.resliceTheResultPoints(mov_points, None, 20, dataset['mov'].getResolution().tolist(), 
            dataset['fix'].getResolution().tolist(), False, R, T)
        resultData.pointSet.data['Contour'] = tmp_con
        dice_index, dice_index_all = self.areaerror.analysis(resultData, fix_points.copy())
        print 'Area Error Done! Whole Dice index is %0.3f.' % dice_index_all
        
        self.sheet3.write(0, i + 2, self.ini.file.name_result[i])
        for j in range(3):
            self.sheet3.write(j + 1, i + 2, mean_dis[j])
            self.sheet3.write(j + 5, i + 2, max_dis[j])
            self.sheet3.write(j + 9, i + 2, dice_index[j])
        self.sheet3.write(4, i + 2, mean_whole)
        self.sheet3.write(8, i + 2, max_whole)
        self.sheet3.write(12, i + 2, dice_index_all)
        self.book.save(self.path + self.ini.file.savedir + 'multicontrast_seg_feature.xls')
        del data, point, resultData
        
        del self.new_points, fix_points, self.new_points_fix, self.new_points_mov, mov_points, tmp_con, result_center_points
         
if __name__ == "__main__":
    test = TestAllRegistration(None)
    test.run()
