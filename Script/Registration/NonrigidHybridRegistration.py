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
import time

from MIRVAP.Script.Analysis.SurfaceErrorAnalysis import SurfaceErrorAnalysis

class NonrigidHybridRegistration(RegistrationBase):
    def __init__(self, gui):
        super(NonrigidHybridRegistration, self).__init__(gui)
    def getName(self):
        return 'Nonrigid Hybrid Registration For Vessel'
                                 
    def register(self, fixedData, movingData, regPara = [(40.0, 1000.0, "SSD")], w2 = 1.0, true_fixed_points = None, true_moving_points = None): # For simple test
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
        
        if true_fixed_points is None:
            true_fixed_points = fixed_points_ori
        if true_moving_points is None:
            true_moving_points = moving_points_ori
        
        fixed_points = fixed_points_ori.copy()
        moving_points = moving_points_ori.copy()
        fixed_points_cen = fixed_points_cen_ori.copy()
        moving_points_cen = moving_points_cen_ori.copy()
        
        fix_img = fixedData.getData()
        mov_img = movingData.getData()
        
        init_time = 0.0
        time1 = time.time()
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
        result_points_cen = result_points_cen[result_points_cen[:, -1] >= 0]
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
        fix_binary_mask = eutil.getBinaryImageFromSegmentation(fix_img, true_fixed_points)
        fix_binary_data = db.BasicData(fix_binary_mask, db.ImageInfo(fixedData.getInfo().data))
        ee.writeImageFile(fix_binary_data, "fixmmm")
        del fix_binary_data
        del fix_binary_mask
        mov_binary_mask = eutil.getBinaryImageFromSegmentation(mov_img, moving_points_ori)
        mov_binary_data = db.BasicData(mov_binary_mask, db.ImageInfo(movingData.getInfo().data))
        ee.writeImageFile(mov_binary_data, "movmm")
        del mov_binary_data
        del mov_binary_mask
        mov_binary_mask = eutil.getBinaryImageFromSegmentation(mov_img, true_moving_points)
        mov_binary_data = db.BasicData(mov_binary_mask, db.ImageInfo(movingData.getInfo().data))
        ee.writeImageFile(mov_binary_data, "movmmm")
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
        ee.writePointsetFile(tmp[crop_moving_index], "movp.txt")
        ee.writePointsetFile(result_points_cen, "fixp.txt")
        
        init_para_inv = eutil.getElastixParaFromMatrix(T_init.I)
        ee.writeTransformFile(init_para_inv, fix_img.shape, fixed_res, type = "MI") # For transformation of image
        ee.writeTransformFile(init_para_inv, fix_img.shape, fixed_res, "transparassd.txt") # For transformation of image
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
        ee.run_executable(type = "transformix", mov = "movmm.mhd", tp = "transparassd.txt", outDir = "")
        ee.renameImage("result", "movmm0")
        ee.run_executable(type = "transformix", mov = "movm.mhd", tp = "transparassd.txt", outDir = "")
        ee.renameImage("result", "movm0")
        ee.run_executable(type = "transformix", mov = "movmmm.mhd", tp = "transparassd.txt", outDir = "")
        ee.renameImage("result", "movmmm0")
        
        sa = SurfaceErrorAnalysis(None)
        
        # Start registration of different parameters
        cnt = len(regPara)
        result = npy.zeros([cnt, 3], dtype = npy.float32)
        fix_img_mask = ee.readImageFile("fixmmm.mhd")
        time2 = time.time()
        init_time = time2 - time1
        for i in range(0, cnt):
            if regPara[i][2] == "MI" and regPara[i][1] > 0:
                ww = regPara[i][1] / 1000
            else:
                ww = regPara[i][1]
            
            isRigid = regPara[i][0] < 0
            # Save Elastix registration configuration
            ee.writeParameterFile("para_rigid.txt", "rigid", regPara[i][2], regPara[i][0], ww, w2)
            if not isRigid:
                ee.writeParameterFile("para_spline.txt", "bspline", regPara[i][2], regPara[i][0], ww, w2)
            
            # Use Elastix for hybrid registration
            if isRigid:
                para_elastix = ["para_rigid.txt"]
            else:
                para_elastix = ["para_rigid.txt", "para_spline.txt"]
            
            if regPara[i][2] == "SSD":
                mov_name = "movmm0.mhd"
                fix_name = "fixmm.mhd"
            else:
                mov_name = "mov0.mhd"
                fix_name = "fix.mhd"
            time1 = time.time()
            code = ee.run_executable(type = "elastix", para = para_elastix, 
                fix = fix_name, mov = mov_name, movm = "movm0.mhd", movp = "movp0.txt", mask = (regPara[i][2] != "SSD"))
            time2 = time.time()
            if code != 0:
                print "Elastix error!"
                continue
            
            # Read the output files into self data formats
            ee.changeOutputBSplineOrder("Output/TransformParameters.0.txt", 0)
            if not isRigid:
                ee.changeOutputBSplineOrder("Output/TransformParameters.1.txt", 0)
                ee.run_executable(type = "transformix", mov = "movmmm0.mhd", tp = "Output/TransformParameters.1.txt") # Non-rigid transformation
                ee.changeOutputInitTransform("Output/TransformParameters.1.txt")
            else:
                ee.run_executable(type = "transformix", mov = "movmmm0.mhd", tp = "Output/TransformParameters.0.txt")
                ee.changeOutputBSplineOrder("Output/TransformParameters.0.txt", 0)
                
            result_img_mask = ee.readImageFile("Output/result.mhd")
            if regPara[i][2] == "SSD":
                # Transform the segmentation result for evaluation
                '''
                if isRigid:
                    result_img_mask = ee.readImageFile("Output/result.0.mhd")
                else:
                    result_img_mask = ee.readImageFile("Output/result.1.mhd")
                '''
                if cnt == 1:
                #if True:
                    ee.changeOutputBSplineOrder("Output/TransformParameters.0.txt", 3)
                    if not isRigid:
                        ee.changeOutputBSplineOrder("Output/TransformParameters.1.txt", 3)
                        ee.run_executable(type = "transformix", mov = "mov0.mhd", tp = "Output/TransformParameters.1.txt") # Non-rigid transformation
                        ee.changeOutputInitTransform("Output/TransformParameters.1.txt")
                    else:
                        ee.run_executable(type = "transformix", mov = "mov0.mhd", tp = "Output/TransformParameters.0.txt")
                    
                    result_img = ee.readImageFile("Output/result.mhd")
                    print i, 'SSD'
                
            else:
                if cnt == 1:
                #if True:
                    if isRigid:
                        result_img = ee.readImageFile("Output/result.0.mhd")
                        print i, 'Other'
                    else:
                        result_img = ee.readImageFile("Output/result.1.mhd")
                
                
                
            ee.generateInverseTransformFile("Output/TransformParameters.0.txt", "fix.mhd")
            
            # Delete the mask slice from the moving points
            tmp = true_moving_points.copy()
            for point in movingData.getPointSet('Mask'):
                tmp = npy.delete(tmp, npy.where((npy.abs(tmp[:, 2] - point[2]) < 0.0001) & (npy.round(tmp[:, -1]) == point[3])), axis = 0)
            tmp[:, :3] *= moving_res
            ee.writePointsetFile(tmp, "movm.txt")
            ee.run_executable(type = "transformix", mov = "movm.txt", tp = "transpara2.txt") # Transform the moving segmentation result using initial transformation
            ee.writePointsetFileFromResult("Output/outputpoints.txt", "mov0m.txt")
            ee.run_executable(type = "transformix", mov = "mov0m.txt", tp = "TransformParameters.0.txt") # Transform the moving segmentation result using rigid transformation
            if not isRigid:
                ee.generateInverseTransformFile("Output/TransformParameters.1.txt", "fix.mhd")
                ee.writePointsetFile(ee.readPointsetFile("Output/outputpoints.txt"), "Output/outputpoints2.txt")
                ee.run_executable(type = "transformix", mov = "Output/outputpoints2.txt", tp = "TransformParameters.0.txt") # Non-rigid transformation
            
            result_con = tmp.copy()
            result_con[:, :3] = ee.readPointsetFile("Output/outputpoints.txt")
            result_con[:, :3] /= fixed_res
            
            result_pointset = {'Contour': result_con}
            
            if cnt > 1:
            #if False:
                dataset = db.BasicData(npy.array([[[0]]]), fixedData.getInfo(), result_pointset)
                mean_dis, mean_whole, max_dis, max_whole = sa.analysis(dataset, point_data_fix = true_fixed_points, useResult = True)
                del dataset
                
                dice_index = eutil.calDiceIndexFromMask(fix_img_mask, result_img_mask)
                del result_img_mask
                
                del result_pointset
                del result_con
                    
                result[i, :] = [mean_whole, dice_index, time2 - time1]# + init_time]
                print "Result of spacing %fmm, weight %f and metric %s: %fmm, %f. " % (regPara[i][0], ww, regPara[i][2], mean_whole, dice_index)
            
            '''
            # Save the result
            resultData = db.ResultData(result_img, db.ImageInfo(fixedData.info.data), result_pointset)
            resultData.info.addData('fix', 1)
            resultData.info.addData('move', 2)
            resultData.info.addData('transform', [0, 0, 0])
            db.saveMatData('D:/Python src/MIRVAP/Result/Result' + str(i) + '_37L.mat', [resultData, fixedData, movingData], 0)
            del resultData
            '''
        
        del fix_img_mask
        if cnt > 1:
            result_img = None
            result_pointset = None
        else:
            result = [0, 0, 0]
        return result_img, result_pointset, result
        
