# -*- coding: utf-8 -*-
"""
Created on 2014-08-10

@author: Hengkai Guo
"""

from MIRVAP.Script.MacroBase import MacroBase
import MIRVAP.Core.DataBase as db
from util.dict4ini import DictIni
from MIRVAP.Script.Registration.NonrigidHybridRegistration import NonrigidHybridRegistration
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCenterlineFromContour
import xlwt
import os, sys

class TestNonrigidRegistration(MacroBase):
    def getName(self):
        return 'Test Different Parameters of Non-rigid Registration'
    def run(self, window = None):
        self.path = sys.argv[0]
        if os.path.isfile(self.path):
            self.path = os.path.dirname(self.path)
        
        self.ini = DictIni(self.path + '/Script/Macro/test.ini')
        self.cnt = len(self.ini.file.name_fix)
        
        self.spacing = [-1.0, 40.0, 32.0, 16.0, 8.0, 4.0]
        self.w1 = [-1.0, 0.0, 1.0, 10.0, 100.0, 1000.0, 10000.0]
        self.type = ['SSD', 'MI', 'CR']
        n = len(self.w1) * len(self.spacing)
        
        self.savepath = self.path + self.ini.file.savedir
        self.book = xlwt.Workbook()
        
        self.sheet1 = self.book.add_sheet('DSC')
        p = 1
        for k in range(len(self.type)):
            self.sheet1.write(p, 0, self.type[k])
            for i in range(len(self.spacing)):
                for j in range(len(self.w1)):
                    self.sheet1.write(p, 1, "beta = %fmm, w1 = %f" % (self.spacing[i], self.w1[j]))
                    p += 1
        
        self.sheet2 = self.book.add_sheet('MSD')
        p = 1
        for k in range(len(self.type)):
            self.sheet2.write(p, 0, self.type[k])
            for i in range(len(self.spacing)):
                for j in range(len(self.w1)):
                    self.sheet2.write(p, 1, "beta = %fmm, w1 = %f" % (self.spacing[i], self.w1[j]))
                    p += 1
                    
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
        hybrid = NonrigidHybridRegistration(None)
        print 'Register Data %s with Hybrid Method...' % (self.ini.file.name_result[i])
        if i > 0:
            data, point, para = hybrid.register(dataset['fix'], dataset['mov'], spacing = self.spacing, w1 = self.w1, type = self.type)
        else:
            import numpy as npy
            para = npy.array([[[[ 0.69645882,  0.78723449],
         [ 3.89362526,  0.04121957],
         [ 0.        ,  0.        ]],

        [[ 0.68270195,  0.78163886],
         [ 0.68270195,  0.78163886],
         [ 0.68270195,  0.78163886]],

        [[ 0.68270195,  0.78163886],
         [ 0.68270129,  0.78163886],
         [ 0.68710375,  0.77710146]],

        [[ 0.68270195,  0.78163886],
         [ 0.68268251,  0.78163707],
         [ 0.7372058 ,  0.74712223]],

        [[ 0.68270195,  0.78163886],
         [ 0.68241054,  0.78170574],
         [ 1.0988977 ,  0.61902076]],

        [[ 0.68270195,  0.78163886],
         [ 0.6777091 ,  0.78105557],
         [ 0.        ,  0.        ]],

        [[ 0.68270195,  0.78163886],
         [ 0.67748874,  0.77721262],
         [ 0.        ,  0.        ]]],


       [[[ 0.69645882,  0.78723449],
         [ 4.17375374,  0.03290556],
         [ 0.        ,  0.        ]],

        [[ 0.72514552,  0.81744266],
         [ 0.72438633,  0.81754762],
         [ 0.72438633,  0.81754762]],

        [[ 0.72514552,  0.81744266],
         [ 0.72452658,  0.81741732],
         [ 0.64885813,  0.83430672]],

        [[ 0.72514552,  0.81744266],
         [ 0.72457826,  0.81715095],
         [ 0.64101613,  0.78294843]],

        [[ 0.72514552,  0.81744266],
         [ 0.71909243,  0.81924146],
         [ 1.56544852,  0.54663271]],

        [[ 0.72514552,  0.81744266],
         [ 0.64701211,  0.82985842],
         [ 0.        ,  0.        ]],

        [[ 0.72514552,  0.81744266],
         [ 0.63720113,  0.80481046],
         [ 0.        ,  0.        ]]],


       [[[ 0.69645882,  0.78723449],
         [ 4.55340672,  0.01554822],
         [ 0.        ,  0.        ]],

        [[ 0.72466081,  0.82064372],
         [ 0.72418243,  0.82067144],
         [ 0.72418243,  0.82067144]],

        [[ 0.72466081,  0.82064372],
         [ 0.72405273,  0.82063597],
         [ 0.66695863,  0.83441657]],

        [[ 0.72466081,  0.82064372],
         [ 0.72342521,  0.82073247],
         [ 0.63968718,  0.79049402]],

        [[ 0.72466081,  0.82064372],
         [ 0.71110106,  0.81960642],
         [ 1.66668832,  0.53745389]],

        [[ 0.72466081,  0.82064372],
         [ 0.6648286 ,  0.82889587],
         [ 0.        ,  0.        ]],

        [[ 0.72466081,  0.82064372],
         [ 0.63549089,  0.8177079 ],
         [ 0.        ,  0.        ]]],


       [[[ 0.69645882,  0.78723449],
         [ 4.72360659,  0.01511557],
         [ 0.        ,  0.        ]],

        [[ 0.82380772,  0.7928049 ],
         [ 0.8224194 ,  0.79308683],
         [ 0.8224194 ,  0.79308683]],

        [[ 0.82380772,  0.7928049 ],
         [ 0.82206762,  0.79309767],
         [ 0.71168554,  0.82505566]],

        [[ 0.82380772,  0.7928049 ],
         [ 0.82073736,  0.7933898 ],
         [ 0.62520307,  0.82659054]],

        [[ 0.82380772,  0.7928049 ],
         [ 0.78542978,  0.80190474],
         [ 1.75900674,  0.54013485]],

        [[ 0.82380772,  0.7928049 ],
         [ 0.71626818,  0.81445503],
         [ 0.        ,  0.        ]],

        [[ 0.82380772,  0.7928049 ],
         [ 0.67024595,  0.8325187 ],
         [ 0.        ,  0.        ]]],


       [[[ 0.69645882,  0.78723449],
         [ 5.45527697,  0.01674968],
         [ 0.        ,  0.        ]],

        [[ 0.98887533,  0.73876411],
         [ 0.98918563,  0.7380994 ],
         [ 0.98918563,  0.7380994 ]],

        [[ 0.98887533,  0.73876411],
         [ 0.98946851,  0.7380994 ],
         [ 0.83188701,  0.78454202]],

        [[ 0.98887533,  0.73876411],
         [ 0.98864555,  0.73846573],
         [ 0.73582125,  0.79609638]],

        [[ 0.98887533,  0.73876411],
         [ 0.97338253,  0.74199653],
         [ 3.60072899,  0.38748357]],

        [[ 0.98887533,  0.73876411],
         [ 0.86681914,  0.78102958],
         [ 0.        ,  0.        ]],

        [[ 0.98887533,  0.73876411],
         [ 0.74885494,  0.81950003],
         [ 0.        ,  0.        ]]],


       [[[ 0.69645882,  0.78723449],
         [ 5.52207136,  0.01433858],
         [ 0.        ,  0.        ]],

        [[ 0.92072237,  0.76365858],
         [ 0.9309622 ,  0.76374525],
         [ 0.9309622 ,  0.76374525]],

        [[ 0.92072237,  0.76365858],
         [ 0.93110389,  0.76381576],
         [ 0.95264024,  0.79304338]],

        [[ 0.92072237,  0.76365858],
         [ 0.93068248,  0.7643488 ],
         [ 2.28922319,  0.61539382]],

        [[ 0.92072237,  0.76365858],
         [ 0.92081058,  0.76770794],
         [ 3.52415943,  0.41119799]],

        [[ 0.92072237,  0.76365858],
         [ 0.81715584,  0.80650622],
         [ 0.        ,  0.        ]],

        [[ 0.92072237,  0.76365858],
         [ 0.85090351,  0.77819759],
         [ 0.        ,  0.        ]]]], dtype=npy.float32)
        print 'Done!'
        
        p = 1
        for k in range(len(self.type)):
            for q in range(len(self.spacing)):
                for j in range(len(self.w1)):
                    self.sheet1.write(p, i + 2, float(para[q, j, k, 0]))
                    self.sheet2.write(p, i + 2, float(para[q, j, k, 1]))
                    p += 1
        
        self.sheet1.write(0, i + 2, self.ini.file.name_result[i])
        self.sheet2.write(0, i + 2, self.ini.file.name_result[i])
        self.book.save(self.path + self.ini.file.savedir + self.ini.file.name + '.xls')
        del para
        del hybrid
