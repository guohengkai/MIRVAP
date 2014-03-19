# -*- coding: utf-8 -*-
"""
Created on 2014-03-16

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import MIRVAP.ThirdParty.gmmreg.executeGmmreg as eg
import numpy as npy

class GmmregPointsetRegistration(RegistrationBase):
    def __init__(self, gui):
        super(GmmregPointsetRegistration, self).__init__(gui)
    def getName(self):
        return 'GMMREG Pointset Registration For Vessel'
                                 
    def register(self, fixedData, movingData):
        fixed_points = fixedData.getPointSet('Contour')
        moving_points = movingData.getPointSet('Contour')
        
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        fixed_points = fixed_points.copy()[npy.where(fixed_points[:, 0] >= 0)]
        moving_points = moving_points.copy()[npy.where(moving_points[:, 0] >= 0)]
        # Use the bifurcation as the initial position
        fixed_bif = db.getBifurcation(fixed_points)
        moving_bif = db.getBifurcation(moving_points)
        if (fixed_bif < 0) or (moving_bif < 0):
            fixed_min = 0
        else:
            temp = moving_points[:, 2:]
            moving_delta = moving_bif - npy.min(moving_points[npy.where(npy.round(temp[:, 1]) == 0), 0])
            fixed_min = fixed_bif - moving_delta * moving_res[-1] / fixed_res[-1]
        
        fixed = fixed_points[npy.where(fixed_points[:, 2] >= fixed_min)]
        fixed = fixed[:, :3]
        moving = moving_points[:, :3]
        fixed[:, :3] *= fixed_res[:3]
        moving[:, :3] *= moving_res[:3]
        fixed[:, 2] -= (fixed_bif * fixed_res[2] - moving_bif * moving_res[2]);
        
        eg.initial_data(fixed, moving)
        code = eg.run_executable()
        if code != 0:
            return None, None
        trans, para = eg.get_final_result()
        print para
        
        trans_points = trans;
        trans_points[:, 2] += (fixed_bif * fixed_res[2] - moving_bif * moving_res[2]);
        trans_points[:, :3] /= fixed_res[:3]
        trans_points = npy.insert(trans, [trans.shape[1]], moving_points[:, -1].reshape(-1, 1), axis = 1)
        trans_points = npy.append(trans_points, npy.array([[-1, -1, -1, -1]]), axis = 0)
        
        # Clear the temp files
        #eg.clear_temp_file()
        
        return fixedData.getData() + 50, {'Contour': trans_points}
