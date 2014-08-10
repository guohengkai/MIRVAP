# -*- coding: utf-8 -*-
"""
Created on 2014-08-03

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

from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis

class NonrigidHybridRegistration(RegistrationBase):
    def __init__(self, gui):
        super(NonrigidHybridRegistration, self).__init__(gui)
    def getName(self):
        return 'Nonrigid Hybrid Registration For Vessel'
                                 
    def register(self, fixedData, movingData, spacing = [40], w1 = [100.0, 1000.0], w2 = 1.0, type = ["SSD"]): # For simple test
        # Initial data
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        
        fixed_points = fixedData.getPointSet('Contour')
        moving_points = movingData.getPointSet('Contour')
        fixed_points_cen = fixedData.getPointSet('Centerline')
        moving_points_cen = movingData.getPointSet('Centerline')
        
        fixed_points_ori = fixed_points.copy()[npy.where(fixed_points[:, 0] >= 0)]
        moving_points_ori = moving_points.copy()[npy.where(moving_points[:, 0] >= 0)]
        fixed_points_cen_ori = fixed_points_cen.copy()[npy.where(fixed_points_cen[:, 0] >= 0)]
        moving_points_cen_ori = moving_points_cen.copy()[npy.where(moving_points_cen[:, 0] >= 0)]
        
        fixed_points = fixed_points_ori.copy()
        moving_points = moving_points_ori.copy()
        fixed_points_cen = fixed_points_cen_ori.copy()
        moving_points_cen = moving_points_cen_ori.copy()
        
        fix_img = fixedData.getData()
        mov_img = movingData.getData()
        
        # Calculate the initial rigid transformation for 9 points T0
        fix_key_point = eutil.getKeyPoints(fixed_points_cen, fixed_res)
        mov_key_point = eutil.getKeyPoints(moving_points_cen, moving_res)
        T0, mov_bif = eutil.getRigidTransform(fix_key_point, mov_key_point) # 4 * 4 Matrix
        moving_points = eutil.applyRigidTransformOnPoints(moving_points, moving_res, T0)
        moving_points_cen_result = eutil.applyRigidTransformOnPoints(moving_points_cen, moving_res, T0)
        crop_fixed_index, crop_moving_index = eutil.cropCenterline(fixed_points_cen, moving_points_cen_result, fixed_res, moving_res, fix_key_point[0, 2] / fixed_res[2], mov_bif[2] / moving_res[2])
        
        # Use GMMREG for centerline-based rigid registration T1
        gmm = GmmregPointsetRegistration(self.gui)
        new_fixedData = db.BasicData(fix_img, db.ImageInfo(fixedData.getInfo().data), 
            {'Contour': fixed_points, 'Centerline': fixed_points_cen[crop_fixed_index]})
        new_movingData = db.BasicData(mov_img, db.ImageInfo(movingData.getInfo().data), 
            {'Contour': moving_points, 'Centerline': moving_points_cen_result[crop_moving_index]})
        tmp_img, points, para = gmm.register(new_fixedData, new_movingData, 1, False, "rigid")
        T1 = eutil.getMatrixFromGmmPara(para)
        T_init = T0 * T1
        moving_points = points['Contour'].copy()
        moving_points_cen_result = points['Centerline'].copy()
        del new_movingData
        
        # Use GMMREG for centerline-based TPS registration
        new_movingData = db.BasicData(mov_img, db.ImageInfo(fixedData.getInfo().data), 
            {'Contour': moving_points, 'Centerline': moving_points_cen_result}) # The image has been resampled into fixed resolution
        tmp_img, points, para = gmm.register(new_fixedData, new_movingData, 1, False, "EM_TPS")
        result_points_cen = points['Centerline'].copy()
        result_points_cen = result_points_cen[result_points_cen[:, 0] >= 0]
        result_points_cen[:, :3] *= fixed_res
        del new_movingData
        del new_fixedData
        del moving_points_cen_result
        
        # Save the images for Elastix registration
        ee.writeImageFile(fixedData, "fix")
        ee.writeImageFile(movingData, "mov")
        fix_binary_mask = eutil.getBinaryImageFromSegmentation(fix_img, fixed_points_ori)
        fix_binary_data = db.BasicData(fix_binary_mask, db.ImageInfo(fixedData.getInfo().data))
        ee.writeImageFile(fix_binary_data, "fixmm")
        del fix_binary_data
        del fix_binary_mask
        mov_binary_mask = eutil.getBinaryImageFromSegmentation(mov_img, moving_points_ori)
        mov_binary_data = db.BasicData(mov_binary_mask, db.ImageInfo(movingData.getInfo().data))
        ee.writeImageFile(mov_binary_data, "movmm")
        del mov_binary_data
        del mov_binary_mask
        
        fix_binary_mask = eutil.getMaskFromCenterline(fix_img, fixed_points_cen_ori, fixed_res)
        fix_binary_data = db.BasicData(fix_binary_mask, db.ImageInfo(fixedData.getInfo().data))
        ee.writeImageFile(fix_binary_data, "fixm")
        del fix_binary_data
        del fix_binary_mask
        mov_binary_mask = eutil.getMaskFromCenterline(mov_img, moving_points_cen_ori, moving_res)
        mov_binary_data = db.BasicData(mov_binary_mask, db.ImageInfo(movingData.getInfo().data))
        ee.writeImageFile(mov_binary_data, "movm")
        del mov_binary_data
        del mov_binary_mask
        
        tmp = moving_points_cen.copy()
        tmp[:, :3] *= moving_res
        ee.writePointsetFile(tmp, "movp.txt")
        ee.writePointsetFile(result_points_cen, "fixp.txt")
        
        init_para_inv = eutil.getElastixParaFromMatrix(T_init.I)
        ee.writeTransformFile(init_para_inv, fix_img.shape, fixed_res, type = type) # For transformation of image
        init_para = eutil.getElastixParaFromMatrix(T_init)
        ee.writeTransformFile(init_para, fix_img.shape, fixed_res, "transpara2.txt") # For transformation of points
        
        # Apply the initial transformation (It seems -t0 didn't work in Elastix)
        ee.run_executable(type = "transformix", mov = "movp.txt", tp = "transpara2.txt")
        ee.writePointsetFileFromResult("Output/outputpoints.txt", "movp0.txt")
        
        tmp = moving_points_ori.copy()
        tmp[:, :3] *= moving_res
        ee.writePointsetFile(tmp, "mov.txt")
        ee.run_executable(type = "transformix", mov = "mov.txt", tp = "transpara2.txt") # Transform the moving segmentation result using initial transformation
        ee.writePointsetFileFromResult("Output/outputpoints.txt", "mov0.txt")
        
        ee.changeOutputBSplineOrder("transpara.txt", 3)
        ee.run_executable(type = "transformix", mov = "mov.mhd", tp = "transpara.txt", outDir = "")
        ee.renameImage("result", "mov0")
        ee.changeOutputBSplineOrder("transpara.txt", 0)
        ee.run_executable(type = "transformix", mov = "movmm.mhd", tp = "transpara.txt", outDir = "")
        ee.renameImage("result", "movmm0")
        ee.run_executable(type = "transformix", mov = "movm.mhd", tp = "transpara.txt", outDir = "")
        ee.renameImage("result", "movm0")
        
        sa = SurfaceErrorAnalysis(None)
        
        # Start registration of different parameters
        cnt = len(spacing) * len(w1) * len(type)
        result = npy.zeros([len(spacing), len(w1), len(type), 2], dtype = npy.float32)
        fix_img_mask = ee.readImageFile("fixmm.mhd")
        for i in range(len(spacing)):
            for k in range(len(type)):
                for j in range(len(w1)):
                    if type[k] == "MI" and w1[j] > 0:
                        ww = w1[j] / 1000
                    else:
                        ww = w1[j]
                    
                    isRigid = spacing[i] < 0
                    # Save Elastix registration configuration
                    ee.writeParameterFile("para_rigid.txt", "rigid", type[k], spacing[i], ww, w2)
                    if not isRigid:
                        ee.writeParameterFile("para_spline.txt", "bspline", type[k], spacing[i], ww, w2)
                    
                    # Use Elastix for hybrid registration
                    if isRigid:
                        para_elastix = ["para_rigid.txt"]
                    else:
                        para_elastix = ["para_rigid.txt", "para_spline.txt"]
                    
                    if type[k] == "SSD":
                        mov_name = "movmm0.mhd"
                        fix_name = "fixmm.mhd"
                    else:
                        mov_name = "mov0.mhd"
                        fix_name = "fix.mhd"
                    code = ee.run_executable(type = "elastix", para = para_elastix, 
                        fix = fix_name, mov = mov_name, movm = "movm0.mhd", movp = "movp0.txt", mask = (type[k] != "SSD"))
                    if code != 0:
                        print "Elastix error!"
                        continue
                        #return None, None, None
                    
                    # Read the output files into self data formats
                    if type[k] == "SSD":
                        # Transform the segmentation result for evaluation
                        if isRigid:
                            result_img_mask = ee.readImageFile("Output/result.0.mhd")
                        else:
                            result_img_mask = ee.readImageFile("Output/result.1.mhd")
                        
                        if cnt == 1:
                            ee.changeOutputBSplineOrder("Output/TransformParameters.0.txt", 3)
                            if not isRigid:
                                ee.changeOutputBSplineOrder("Output/TransformParameters.1.txt", 3)
                                ee.run_executable(type = "transformix", mov = "mov0.mhd", tp = "Output/TransformParameters.1.txt") # Non-rigid transformation
                                ee.changeOutputInitTransform("Output/TransformParameters.1.txt")
                            else:
                                ee.run_executable(type = "transformix", mov = "mov0.mhd", tp = "Output/TransformParameters.0.txt")
                            
                            result_img = ee.readImageFile("Output/result.mhd")
                        
                    else:
                        if cnt == 1:
                            if isRigid:
                                result_img = ee.readImageFile("Output/result.0.mhd")
                            else:
                                result_img = ee.readImageFile("Output/result.1.mhd")
                        
                        ee.changeOutputBSplineOrder("Output/TransformParameters.0.txt", 0)
                        if not isRigid:
                            ee.changeOutputBSplineOrder("Output/TransformParameters.1.txt", 0)
                            ee.run_executable(type = "transformix", mov = "movmm0.mhd", tp = "Output/TransformParameters.1.txt") # Non-rigid transformation
                            ee.changeOutputInitTransform("Output/TransformParameters.1.txt")
                        else:
                            ee.run_executable(type = "transformix", mov = "movmm0.mhd", tp = "Output/TransformParameters.0.txt")
                        
                        result_img_mask = ee.readImageFile("Output/result.mhd")
                        
                    ee.generateInverseTransformFile("Output/TransformParameters.0.txt", "fix.mhd")
                    ee.run_executable(type = "transformix", mov = "mov0.txt", tp = "TransformParameters.0.txt") # Transform the moving segmentation result using rigid transformation
                    if not isRigid:
                        ee.generateInverseTransformFile("Output/TransformParameters.1.txt", "fix.mhd")
                        ee.writePointsetFile(ee.readPointsetFile("Output/outputpoints.txt"), "Output/outputpoints2.txt")
                        ee.run_executable(type = "transformix", mov = "Output/outputpoints2.txt", tp = "TransformParameters.0.txt") # Non-rigid transformation
                    
                    result_con = moving_points_ori.copy()
                    result_con[:, :3] = ee.readPointsetFile("Output/outputpoints.txt")
                    result_con[:, :3] /= fixed_res
                    
                    result_pointset = {'Contour': result_con}
                    
                    if cnt > 1:
                        dataset = db.BasicData(None, fixedData.getInfo(), result_pointset)
                        mean_dis, mean_whole, max_dis, max_whole = sa.analysis(dataset, point_data_fix = fixedData.getPointSet('Contour').copy(), useResult = True)
                        del dataset
                        
                        dice_index = eutil.calDiceIndexFromMask(fix_img_mask, result_img_mask)
                        #del fix_img_mask
                        del result_img_mask
                        
                        del result_pointset
                        del result_con
                            
                        result[i, j, k, :] = [mean_whole, dice_index]
                        print "Result of spacing %fmm, weight %f and metric %s: %fmm, %f. " % (spacing[i], ww, type[k], mean_whole, dice_index)
                    
        if cnt > 1:
            result_img = None
            result_pointset = None
        else:
            result = [0, 0, 0]
        return result_img, result_pointset, result
        
