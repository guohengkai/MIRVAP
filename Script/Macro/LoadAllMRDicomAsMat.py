# -*- coding: utf-8 -*-
"""
Created on 2014-05-10

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from MIRVAP.Script.Load.LoadDicomFile import LoadDicomFile
from util.dict4ini import DictIni

import os, sys

class LoadAllMRDicomAsMat(MacroBase):
    def getName(self):
        return 'Load All MR data as mat files'
    def load(self):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        self.path = self.path.replace('\\', '/')
        
        self.ini = DictIni(self.path + '/Script/Macro/load.ini')
        load = LoadDicomFile(None)
        
        dataset = [None, None]
        self.cnt = self.ini.file.name_result
        dir = self.path + self.ini.file.datadir + 'crop' + str(self.cnt) + '/'
        mdir = dir + "3D Merge/"
        namelist = os.listdir(mdir)
        dataset = load.load([str(mdir.replace('/', '\\') + x) for x in namelist])[0]
        dataset.setName('Patient%d_Merge_Full' % self.cnt)
        print '3D Merge Data %d loaded!' % self.cnt
            
        return dataset
    def process(self, dataset):
        savepath = self.path + self.ini.file.savedir
        db.saveMatData(savepath + 'MR_%d_Merge_Full.mat' % self.cnt, dataset, 0)
        db.saveMatData(savepath + 'MR_%d_SNAP_Full.mat' % self.cnt, dataset, 1)
         
if __name__ == "__main__":
    test = LoadAllMRDicomAsMat(None)
    test.run()
