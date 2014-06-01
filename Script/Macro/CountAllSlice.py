# -*- coding: utf-8 -*-
"""
Created on 2014-05-26

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
import numpy as npy
from util.dict4ini import DictIni
import os, sys
import xlwt

class CountAllSlice(MacroBase):
    def getName(self):
        return 'Count All Slice'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        self.uspoints = 0
        self.usslices = 0
        self.mrpoints = 0
        self.mrslices = 0
        self.book = xlwt.Workbook()
        title = ['Bottom', 'Bifurcation', 'Top', 'X', 'Y', 'Z']
        self.sheet_us = self.book.add_sheet('US')
        for i in range(1, 7):
            self.sheet_us.write(0, i, title[i - 1])
        self.sheet_mr = self.book.add_sheet('MR')
        for i in range(1, 7):
            self.sheet_mr.write(0, i, title[i - 1])
        
        for i in range(self.cnt):
            dataset = self.load(i)
            self.process(dataset, i)
            del dataset
        if self.gui:
            self.gui.showErrorMessage('Success', 'US Slice: %d, US Point: %d\nMR Slice: %d, MR Point: %d\nTotal Slice: %d, Total Point: %d\n' 
                % (self.usslices, self.uspoints, self.mrslices, self.mrpoints, self.usslices + self.mrslices, self.uspoints + self.mrpoints))
        else:
            print 'Test sucessfully!'
            
    def load(self, i):
        dataset = {'us': [], 'mr': []}
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir
            + self.ini.file.name_fix[i] + '.mat', None)
        fileData = db.BasicData(data, info, point)
        dataset['mr'] = fileData
        
        data, info, point = db.loadMatData(self.path + self.ini.file.datadir
            + self.ini.file.name_mov[i] + '.mat', None)
        fileData = db.BasicData(data, info, point)
        dataset['us'] = fileData
        print 'Data %s loaded!' % self.ini.file.name_result[i]
            
        return dataset
    def process(self, dataset, i):
        point_us = dataset['us'].pointSet.data['Contour']
        point_us = point_us[point_us[:, 0] >= 0][:, 2]
        point_mr = dataset['mr'].pointSet.data['Contour']
        point_mr = point_mr[point_mr[:, 0] >= 0][:, 2]
        
        bottom_us = npy.min(point_us)
        top_us = npy.max(point_us)
        bif_us = db.getBifurcation(dataset['us'].pointSet.data['Contour'])
        res_us = dataset['us'].getResolution()
        
        bottom_mr = npy.min(point_mr)
        top_mr = npy.max(point_mr)
        bif_mr = db.getBifurcation(dataset['mr'].pointSet.data['Contour'])
        res_mr = dataset['mr'].getResolution()
        
        self.usslices += top_us - bottom_us + 1
        self.uspoints += point_us.shape[0]
        self.mrslices += top_mr - bottom_mr + 1
        self.mrpoints += point_mr.shape[0]
        
        self.sheet_us.write(i + 1, 0, self.ini.file.name_result[i])
        self.sheet_us.write(i + 1, 1, bottom_us)
        self.sheet_us.write(i + 1, 2, bif_us)
        self.sheet_us.write(i + 1, 3, top_us)
        for j in range(3):
            self.sheet_us.write(i + 1, j + 4, res_us[j])
        
        self.sheet_mr.write(i + 1, 0, self.ini.file.name_result[i])
        self.sheet_mr.write(i + 1, 1, bottom_mr)
        self.sheet_mr.write(i + 1, 2, bif_mr)
        self.sheet_mr.write(i + 1, 3, top_mr)
        for j in range(3):
            self.sheet_mr.write(i + 1, j + 4, res_mr[j])
        
        self.book.save('./Result/count.xls')
         
if __name__ == "__main__":
    test = CountAllSlice(None)
    test.run()
