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
    f.writeline('point')
    f.writeline(pointset.shape[0])
    for point in pointset:
        f.writeline("%f %f %f" % tuple(point[:3]))
    f.close()
    
def readPointsetFile(file_name):
    f = open(get_exe_path() + "/" + file_name, 'r')
    
    # TO BE DONE
    
    f.close()
    
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
    
    f.writeline('(FixedInternalImagePixelType "float")')
    f.writeline('(MovingInternalImagePixelType "float")')
    f.writeline('(UseDirectionCosines "false")')
    
    # Main Components
    f.writeline('(Registration "MultiResolutionRegistration")')
    f.writeline('(Interpolator "BSplineInterpolator")')
    f.writeline('(ResampleInterpolator "FinalBSplineInterpolator")')
    f.writeline('(Resampler "DefaultResampler")')
    
    f.writeline('(FixedImagePyramid "FixedRecursiveImagePyramid")')
    f.writeline('(MovingImagePyramid "MovingRecursiveImagePyramid")')
    
    f.writeline('(Optimizer "AdaptiveStochasticGradientDescent")')
    f.writeline('(Transform "%s")' % trans)
    f.writeline('(Metric "%s" "CorrespondingPointsEuclideanDistanceMetric")' % metric)
    f.writeline('(Metric0Weight %f)' % w1)
    f.writeline('(Metric1Weight %f)' % w2)
    
    # Transformation
    f.writeline('(AutomaticTransformInitialization "true")')
    f.writeline('(AutomaticScalesEstimation "true")')
    f.writeline('(HowToCombineTransforms "Compose")')
    f.writeline('(FinalGridSpacingInPhysicalUnits %d)' % spacing)
    
    # Similarity measure
    f.writeline('(NumberOfHistogramBins 32)')
    f.writeline('(ErodeMask "false")')
    
    # Multiresolution
    f.writeline('(NumberOfResolutions 4)')
    
    # Optimizer
    f.writeline('(MaximumNumberOfIterations 2000)')
    
    # Image sampling
    f.writeline('(NumberOfSpatialSamples 2000)')
    f.writeline('(NewSamplesEveryIteration "true")')
    f.writeline('(ImageSampler "Random")')
    
    # Interpolation and Resampling
    f.writeline('(BSplineInterpolationOrder 1)')
    f.writeline('(FinalBSplineInterpolationOrder 3)')
    f.writeline('(DefaultPixelValue 0)')
    f.writeline('(WriteResultImage "true")')
    f.writeline('(ResultImagePixelType "float")')
    f.writeline('(ResultImageFormat "mhd")')
    
    f.close()
    
def writeTransformFile(para, size, spacing, file_name = "transpara.txt"):
    f = open(get_exe_path() + "/" + file_name, "w")
    
    f.writeline('(Transform "EulerTransform")')
    f.writeline('(NumberOfParameters 6)')
    f.writeline('(TransformParameters %f %f %f %f %f %f)' % tuple(para[:6])) # 3 rotation angles, translation vetor
    f.writeline('(InitialTransformParametersFileName "NoInitialTransform")')
    f.writeline('(HowToCombineTransforms "Compose")')
    
    # Image specific
    f.writeline('(FixedImageDimension 3)')
    f.writeline('(MovingImageDimension 3)')
    f.writeline('(FixedInternalImagePixelType "float")')
    f.writeline('(MovingInternalImagePixelType "float")')
    f.writeline('(Size %d %d %d)' % tuple(size))
    f.writeline('(Index 0 0)')
    f.writeline('(Spacing %f %f %f)' % tuple(spacing))
    f.writeline('(Origin 0.0000000000 0.0000000000)')
    
    # EulerTransform specific
    f.writeline('(CenterOfRotationPoint %f %f %f)' % tuple(para[-3:]))
    
    # ResampleInterpolator specific
    f.writeline('(ResampleInterpolator "FinalBSplineInterpolator")')
    f.writeline('(FinalBSplineInterpolationOrder 3)')
    
    # Resampler specific
    f.writeline('(Resampler "DefaultResampler")')
    f.writeline('(DefaultPixelValue 0)')
    f.writeline('(ResultImagePixelType "float")')
    f.writeline('(ResultImageFormat "mhd")')
    
    f.close()
