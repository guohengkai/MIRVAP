# -*- coding: utf-8 -*-
"""
Created on 2014-03-16

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import itk

class PointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(PointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'Pointset Registration'
                                 
    def register(self, fixedData, movingData):
        traitstype = itk.DefaultStaticMeshTraits[itk.D, 3, 3, itk.D]
        pointset_type = itk.PointSet[itk.D, 3, traitstype]
        
        fixed_pointset = pointset_type.New()
        moving_pointset = pointset_type.New()
        
        # pointset.SetPoint(id, [x, y, z])
        # pp = point_type()
        # pointset.GetPoint(id, pp)
        # pp.GetElement(0)
        
        fixed_points = fixedData.getPointSet('Centerline')
        moving_points = movingData.getPointSet('Centerline')
        
        cnt = 0
        id = 0
        for x in fixed_points:
            if x[-1] == cnt:
                fixed_pointset.SetPoint(id, [x[0], x[1], x[2]])
                id += 1
        
        id = 0
        for x in moving_points:
            if x[-1] == cnt:
                moving_pointset.SetPoint(id, [x[0], x[1], x[2]])
                id += 1
                
        metric_type = itk.EuclideanDistance[pointset_type, pointset_type]
        
        point_type = itk.Point[itk.D, 3]
        
        resultData = db.ResultData()
        resultData.setDataFromITKImage(outputImage, image_type)
        return resultData
