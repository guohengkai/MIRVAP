# -*- coding: utf-8 -*-
"""
Created on 2014-08-03

@author: Hengkai Guo
"""

import sys, os
import subprocess
import ConfigParser
import numpy as npy
import MIRVAP.Core.DataBase as db

# elastix or transformix
def run_executable(exe = None, type = "elastix", fix = "fix.mhd", mov = "mov.mhd", fixm = "fixm.mhd", movm = "movm.mhd", 
        fixp = "fixp.txt", movp = "movp.txt", outDir = "Output/", para = ["para.txt"], tp = "transpara.txt"):
    if exe is None:
        exe = "%s.exe" % type
    gen_path = get_exe_path() + "/"
    if type == "elastix":
        cmd = '"%s" -f "%s" -m "%s" -out "%s" -fp "%s" -mp "%s" -t0 "%s" -fMask "%s" -mMask "%s"' % \
            (gen_path + exe, gen_path + fix, gen_path + mov, gen_path + outDir, 
            gen_path + para, gen_path + fixp, gen_path + movp, gen_path + tp, 
            gen_path + fixm, gen_path + movm)
        for p in para:
            cmd += ' -p "%s"' % (gen_path + p)
    elif type == "transformix":
        if mov[-3:] == 'mhd':
            input_type = "in"
        elif mov[-3:] == 'txt':
            input_type = "def"
        else:
            return -1
        cmd = '"%s" -%s "%s" -out "%s" -tp "%s"' % \
            (gen_path + exe, input_type, gen_path + mov, gen_path + outDir, gen_path + tp)
    else:
        return -1
    print cmd
    return subprocess.call(cmd, shell = True)

def get_exe_path():
    path = sys.argv[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
        
    path += '/ThirdParty/Elastix'
    #print path
    return path
    
def writeImageFile(image, file_name):
    db.saveRawData(get_exe_path() + "/" + file_name, [image], 0)
    
def readImageFile(file_name):
    return db.readRawData(get_exe_path() + "/" + file_name)
    
def writePointsetFile(pointset, file_name = "point.txt"):
    f = open(get_exe_path() + "/" + file_name, 'w')
    f.writelines('point')
    f.writelines(pointset.shape[0])
    for point in pointset:
        f.writelines("%f %f %f" % tuple(point[:3]))
    f.close()
    
def readPointsetFile(file_name):
    f = open(get_exe_path() + "/" + file_name, 'r')
    
    s = f.readline() # 'point'
    s = f.readline()
    n = int(s)

    pointset = npy.zeros([n, 3], dtype = npy.float32)
    i = 0
    for s in f.readlines():
        point = s.split(' ')
        pointset[i, :] = map(float, point)
        i += 1
        
    f.close()

    return pointset
    
def writeParameterFile(file_name = "para.txt", trans_type = "rigid", metric_type = "MI", spacing = 20, w1 = 1.0, w2 = 1.0):
    if trans_type == "rigid":
        trans = "EulerTransform"
    elif trans_type == "bspline":
        trans = "BSplineTransform"
    else:
        return
        
    if metric_type == "MI":
        metric = "AdvancedMattesMutualInformation"
    elif metric_type == "CR":
        metric = "AdvancedNormalizedCorrelation"
    elif metric_type == "SSD":
        metric = "AdvancedMeanSquares"
    else:
        return
    
    f = open(get_exe_path() + "/" + file_name, "w")
    
    f.writelines('(FixedInternalImagePixelType "float")')
    f.writelines('(MovingInternalImagePixelType "float")')
    f.writelines('(UseDirectionCosines "false")')
    
    # Main Components
    f.writelines('(Registration "MultiResolutionRegistration")')
    f.writelines('(Interpolator "BSplineInterpolator")')
    f.writelines('(ResampleInterpolator "FinalBSplineInterpolator")')
    f.writelines('(Resampler "DefaultResampler")')
    
    f.writelines('(FixedImagePyramid "FixedRecursiveImagePyramid")')
    f.writelines('(MovingImagePyramid "MovingRecursiveImagePyramid")')
    
    f.writelines('(Optimizer "AdaptiveStochasticGradientDescent")')
    f.writelines('(Transform "%s")' % trans)
    f.writelines('(Metric "%s" "CorrespondingPointsEuclideanDistanceMetric")' % metric)
    f.writelines('(Metric0Weight %f)' % w1)
    f.writelines('(Metric1Weight %f)' % w2)
    
    # Transformation
    f.writelines('(AutomaticTransformInitialization "true")')
    f.writelines('(AutomaticScalesEstimation "true")')
    f.writelines('(HowToCombineTransforms "Compose")')
    f.writelines('(FinalGridSpacingInPhysicalUnits %d)' % spacing)
    
    # Similarity measure
    f.writelines('(NumberOfHistogramBins 32)')
    f.writelines('(ErodeMask "false")')
    
    # Multiresolution
    f.writelines('(NumberOfResolutions 4)')
    
    # Optimizer
    f.writelines('(MaximumNumberOfIterations 2000)')
    
    # Image sampling
    f.writelines('(NumberOfSpatialSamples 2000)')
    f.writelines('(NewSamplesEveryIteration "true")')
    f.writelines('(ImageSampler "Random")')
    
    # Interpolation and Resampling
    f.writelines('(BSplineInterpolationOrder 1)')
    f.writelines('(FinalBSplineInterpolationOrder 3)')
    f.writelines('(DefaultPixelValue 0)')
    f.writelines('(WriteResultImage "true")')
    f.writelines('(ResultImagePixelType "float")')
    f.writelines('(ResultImageFormat "mhd")')
    
    f.close()
    
def writeTransformFile(para, size, spacing, file_name = "transpara.txt"):
    f = open(get_exe_path() + "/" + file_name, "w")
    
    f.writelines('(Transform "EulerTransform")')
    f.writelines('(NumberOfParameters 6)')
    f.writelines('(TransformParameters %f %f %f %f %f %f)' % tuple(para[:6])) # 3 rotation angles, translation vetor
    f.writelines('(InitialTransformParametersFileName "NoInitialTransform")')
    f.writelines('(HowToCombineTransforms "Compose")')
    
    # Image specific
    f.writelines('(FixedImageDimension 3)')
    f.writelines('(MovingImageDimension 3)')
    f.writelines('(FixedInternalImagePixelType "float")')
    f.writelines('(MovingInternalImagePixelType "float")')
    f.writelines('(Size %d %d %d)' % tuple(size))
    f.writelines('(Index 0 0)')
    f.writelines('(Spacing %f %f %f)' % tuple(spacing))
    f.writelines('(Origin 0.0000000000 0.0000000000)')
    
    # EulerTransform specific
    f.writelines('(CenterOfRotationPoint %f %f %f)' % tuple(para[-3:]))
    
    # ResampleInterpolator specific
    f.writelines('(ResampleInterpolator "FinalBSplineInterpolator")')
    f.writelines('(FinalBSplineInterpolationOrder 3)')
    
    # Resampler specific
    f.writelines('(Resampler "DefaultResampler")')
    f.writelines('(DefaultPixelValue 0)')
    f.writelines('(ResultImagePixelType "float")')
    f.writelines('(ResultImageFormat "mhd")')
    
    f.close()
