# -*- coding: utf-8 -*-
"""
Created on 2015-04-12

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
from MIRVAP.GUI.qvtk.Plugin.util.PluginUtil import calCentroidFromContour
from MIRVAP.Script.Registration.GmmregPointsetRegistration import GmmregPointsetRegistration
import MIRVAP.Core.DataBase as db
import MIRVAP.ThirdParty.Elastix.executeElastix as ee
import numpy as npy
import numpy.matlib as ml
import itk, vtk
import SimpleITK as sitk
import util.RegistrationUtil as util
import util.Hybrid.ElastixUtil as eutil
import time

from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis

class NonrigidGMMRegistration(RegistrationBase):
    def __init__(self, gui):
        super(NonrigidGMMRegistration, self).__init__(gui)
    def getName(self):
        return 'Nonrigid GMM Registration For Vessel'
                                 
    def register(self, fixedData, movingData, index = -1, isRigid = False, isTime = False): # For simple test
        if index == -1:
            if self.gui is not None:
                index = self.gui.getDataIndex({'Contour': 0, 'Centerline': 1}, 'Select the object')
            else:
                index = 1
        if index is None:
            return None, None, None
        if index == 0:
            fixed_points = fixedData.getPointSet('Contour')
            moving_points = movingData.getPointSet('Contour')
        else:
            fixed_points = fixedData.getPointSet('Centerline')
            moving_points = movingData.getPointSet('Centerline')
        time1 = time.time()
        # Initial data
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        
        fixed_points_con = fixedData.getPointSet('Contour')
        moving_points_con = movingData.getPointSet('Contour')
        fixed_points_cen = fixedData.getPointSet('Centerline')
        moving_points_cen = movingData.getPointSet('Centerline')
        
        fixed_points_ori = fixed_points.copy()[npy.where(fixed_points[:, 0] >= 0)]
        moving_points_ori = moving_points.copy()[npy.where(moving_points[:, 0] >= 0)]
        fixed_points_con_ori = fixed_points_con.copy()[npy.where(fixed_points_con[:, 0] >= 0)]
        moving_points_con_ori = moving_points_con.copy()[npy.where(moving_points_con[:, 0] >= 0)]
        fixed_points_cen_ori = fixed_points_cen.copy()[npy.where(fixed_points_cen[:, 0] >= 0)]
        moving_points_cen_ori = moving_points_cen.copy()[npy.where(moving_points_cen[:, 0] >= 0)]
        
        fixed_points = fixed_points_ori.copy()
        moving_points = moving_points_ori.copy()
        fixed_points_con = fixed_points_con_ori.copy()
        moving_points_con = moving_points_con_ori.copy()
        fixed_points_cen = fixed_points_cen_ori.copy()
        moving_points_cen = moving_points_cen_ori.copy()
        
        init_time = 0.0
        time1 = time.time()
        
        fix_img = fixedData.getData()
        mov_img = movingData.getData()
        
        # Calculate the initial rigid transformation for 9 points T0
        fix_key_point = eutil.getKeyPoints(fixed_points_cen, fixed_res)
        mov_key_point = eutil.getKeyPoints(moving_points_cen, moving_res)
        T0, mov_bif = eutil.getRigidTransform(fix_key_point, mov_key_point) # 4 * 4 Matrix
        moving_points = eutil.applyRigidTransformOnPoints(moving_points, moving_res, T0)
        moving_points_con = eutil.applyRigidTransformOnPoints(moving_points_con, moving_res, T0)
        moving_points_cen_result = eutil.applyRigidTransformOnPoints(moving_points_cen, moving_res, T0)
        crop_fixed_index, crop_moving_index = eutil.cropCenterline(fixed_points_cen, moving_points_cen_result, fixed_res, moving_res, fix_key_point[0, 2] / fixed_res[2], mov_bif[2] / moving_res[2])
        
        # Use GMMREG for centerline-based rigid registration T1
        gmm = GmmregPointsetRegistration(self.gui)
        new_fixedData = db.BasicData(fix_img, db.ImageInfo(fixedData.getInfo().data), 
            {'Contour': fixed_points_con, 'Centerline': fixed_points_cen[crop_fixed_index]})
        new_movingData = db.BasicData(mov_img, db.ImageInfo(movingData.getInfo().data), 
            {'Contour': moving_points_con, 'Centerline': moving_points_cen_result[crop_moving_index]})
        tmp_img, points, para = gmm.register(new_fixedData, new_movingData, index, False, "rigid")
        T1 = eutil.getMatrixFromGmmPara(para)
        T_init = T0 * T1
        moving_points = points['Contour'].copy()
        moving_points_cen_result = points['Centerline'].copy()
        del new_movingData
        
        # Use GMMREG for centerline-based TPS registration
        if not isRigid:
            new_movingData = db.BasicData(mov_img, db.ImageInfo(fixedData.getInfo().data), 
                {'Contour': moving_points, 'Centerline': moving_points_cen_result}) # The image has been resampled into fixed resolution
            tmp_img, points, para = gmm.register(new_fixedData, new_movingData, index, False, "EM_TPS")
        time2 = time.time()
        
        sa = SurfaceErrorAnalysis(None)
        dataset = db.BasicData(npy.array([[[0]]]), fixedData.getInfo(), points)
        mean_dis, mean_whole, max_dis, max_whole = sa.analysis(dataset, point_data_fix = fixed_points_con.copy(), useResult = True)
        del dataset
        print mean_dis
        print mean_whole
        
        if isTime:
            return tmp_img, points, [mean_dis, mean_whole], time2 - time1
        return tmp_img, points, [mean_dis, mean_whole]
        
