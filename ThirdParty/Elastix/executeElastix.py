# -*- coding: utf-8 -*-
"""
Created on 2014-08-03

@author: Hengkai Guo
"""

import sys, os
import re
import subprocess
import ConfigParser
import numpy as npy
import MIRVAP.Core.DataBase as db

# elastix or transformix
def run_executable(exe = None, type = "elastix", fix = "fix.mhd", mov = "mov.mhd", fixm = "fixm.mhd", movm = "movm.mhd", 
        fixp = "fixp.txt", movp = "movp.txt", outDir = "Output/", para = ["para.txt"], tp = "transpara.txt", mask = True, init = False):
    if exe is None:
        exe = "%s.exe" % type
    gen_path = get_exe_path() + "/"
    if type == "elastix":
        cmd = '"%s" -f "%s" -m "%s" -out "%s" -fp "%s" -mp "%s"' % \
            (gen_path + exe, gen_path + fix, gen_path + mov, gen_path + outDir, 
            gen_path + fixp, gen_path + movp)
        for p in para:
            cmd += ' -p "%s"' % (gen_path + p)
        if mask:
            cmd += ' -fMask "%s" -mMask "%s"' % (gen_path + fixm, gen_path + movm)
        if init:
            cmd += ' -t0 "%s"' % (gen_path + tp)
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
    #print cmd
    return subprocess.call(cmd, shell = True)

def get_exe_path():
    path = sys.argv[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
        
    path += '/ThirdParty/Elastix'
    #print path
    return path
    
def writeImageFile(image, file_name):
    data_model = [image]
    db.saveRawData(get_exe_path() + "/" + file_name, data_model, 0)
    del data_model
    
def readImageFile(file_name):
    image, info, point = db.loadRawData(get_exe_path() + "/" + file_name)
    return image
    
def writePointsetFile(pointset, file_name = "point.txt"):
    f = open(get_exe_path() + "/" + file_name, 'w')
    f.write('point' + '\n')
    f.write('%d\n' % pointset.shape[0])
    for point in pointset:
        f.write("%f %f %f" % tuple(point[:3]) + '\n')
    f.close()
    
def readPointsetFile(file_name):
    f = open(get_exe_path() + "/" + file_name, 'r')
    
    lines = f.readlines()
    n = len(lines)
    pointset = npy.zeros([n, 3], dtype = npy.float32)
    pattern = "OutputPoint = \\[ (.*?) (.*?) (.*?) \\]"
    prog = re.compile(pattern)
    i = 0
    for line in lines:
        result = prog.findall(line)
        pointset[i, :] = [float(result[0][0]), float(result[0][1]), float(result[0][2])]
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
    
    f.write('(FixedInternalImagePixelType "float")' + '\n')
    f.write('(MovingInternalImagePixelType "float")' + '\n')
    f.write('(UseDirectionCosines "false")' + '\n')
    
    # Main Components
    f.write('(Registration "MultiMetricMultiResolutionRegistration")' + '\n')
    f.write('(Interpolator "BSplineInterpolator")' + '\n')
    f.write('(ResampleInterpolator "FinalBSplineInterpolator")' + '\n')
    f.write('(Resampler "DefaultResampler")' + '\n')
    
    f.write('(FixedImagePyramid "FixedRecursiveImagePyramid")' + '\n')
    f.write('(MovingImagePyramid "MovingRecursiveImagePyramid")' + '\n')
    
    f.write('(Optimizer "AdaptiveStochasticGradientDescent")' + '\n')
    f.write('(Transform "%s")' % trans + '\n')
    f.write('(Metric "%s" "CorrespondingPointsEuclideanDistanceMetric")' % metric + '\n')
    f.write('(Metric0Weight %f)' % w1 + '\n')
    f.write('(Metric1Weight %f)' % w2 + '\n')
    
    # Transformation
    f.write('(AutomaticTransformInitialization "false")' + '\n')
    f.write('(AutomaticScalesEstimation "true")' + '\n')
    f.write('(HowToCombineTransforms "Compose")' + '\n')
    f.write('(FinalGridSpacingInPhysicalUnits %d)' % spacing + '\n')
    
    # Similarity measure
    f.write('(NumberOfHistogramBins 32)' + '\n')
    f.write('(ErodeMask "false")' + '\n')
    
    # Multiresolution
    f.write('(NumberOfResolutions 4)' + '\n')
    
    # Optimizer
    f.write('(MaximumNumberOfIterations 2000)' + '\n')
    
    # Image sampling
    f.write('(NumberOfSpatialSamples 2000)' + '\n')
    f.write('(NewSamplesEveryIteration "true")' + '\n')
    f.write('(ImageSampler "Random")' + '\n')
    
    # Interpolation and Resampling
    f.write('(BSplineInterpolationOrder 1)' + '\n')
    f.write('(FinalBSplineInterpolationOrder 3)' + '\n')
    f.write('(DefaultPixelValue 0)' + '\n')
    f.write('(WriteResultImage "true")' + '\n')
    f.write('(ResultImagePixelType "float")' + '\n')
    f.write('(ResultImageFormat "mhd")' + '\n')
    
    f.close()
    
def writeTransformFile(para, size, spacing, file_name = "transpara.txt", type = "SSD"):
    if type == "SSD":
        spline_order = 0
    else:
        spline_order = 3
        
    f = open(get_exe_path() + "/" + file_name, "w")
    
    f.write('(Transform "EulerTransform")' + '\n')
    f.write('(NumberOfParameters 6)' + '\n')
    f.write('(TransformParameters %f %f %f %f %f %f)' % tuple(para[:6]) + '\n') # 3 rotation angles, translation vetor
    f.write('(InitialTransformParametersFileName "NoInitialTransform")' + '\n')
    f.write('(HowToCombineTransforms "Compose")' + '\n')
    
    # Image specific
    f.write('(FixedImageDimension 3)' + '\n')
    f.write('(MovingImageDimension 3)' + '\n')
    f.write('(FixedInternalImagePixelType "float")' + '\n')
    f.write('(MovingInternalImagePixelType "float")' + '\n')
    f.write('(Size %d %d %d)' % tuple(size[::-1]) + '\n')
    f.write('(Index 0 0)' + '\n')
    f.write('(Spacing %f %f %f)' % tuple(spacing) + '\n')
    f.write('(Origin 0.0000000000 0.0000000000)' + '\n')
    
    # EulerTransform specific
    f.write('(CenterOfRotationPoint %f %f %f)' % tuple(para[-3:]) + '\n')
    
    # ResampleInterpolator specific
    f.write('(ResampleInterpolator "FinalBSplineInterpolator")' + '\n')
    f.write('(FinalBSplineInterpolationOrder %d)' % spline_order + '\n')
    
    # Resampler specific
    f.write('(Resampler "DefaultResampler")' + '\n')
    f.write('(DefaultPixelValue 0)' + '\n')
    f.write('(ResultImagePixelType "float")' + '\n')
    f.write('(ResultImageFormat "mhd")' + '\n')
    
    f.close()

def writePointsetFileFromResult(input, output):
    writePointsetFile(readPointsetFile(input), output)

def changeOutputBSplineOrder(file_name, order = 0):
    f = open(get_exe_path() + "/" + file_name, "w")
    # TO BE DONE
    
    f.close()
def getTransformName(file_name):
    # TO BE DONE
    return name

def generateInverseTransformFile(file_name, fix_img_name):
    # Write temporary parameter files
    f = open(get_exe_path() + "/tmp_para.txt", "w")
    f.write('(FixedInternalImagePixelType "float")' + '\n')
    f.write('(MovingInternalImagePixelType "float")' + '\n')
    f.write('(UseDirectionCosines "false")' + '\n')
    f.write('(Registration "MultiResolutionRegistration")' + '\n')
    f.write('(Interpolator "BSplineInterpolator")' + '\n')
    f.write('(ResampleInterpolator "FinalBSplineInterpolator")' + '\n')
    f.write('(Resampler "DefaultResampler")' + '\n')
    f.write('(FixedImagePyramid "FixedRecursiveImagePyramid")' + '\n')
    f.write('(MovingImagePyramid "MovingRecursiveImagePyramid")' + '\n')
    f.write('(Optimizer "AdaptiveStochasticGradientDescent")' + '\n')
    f.write('(Transform "%s")' % getTransformName(file_name) + '\n')
    f.write('(Metric "DisplacementMagnitudePenalty")' + '\n')
    f.write('(AutomaticTransformInitialization "false")' + '\n')
    f.write('(AutomaticScalesEstimation "true")' + '\n')
    f.write('(HowToCombineTransforms "Compose")' + '\n')
    f.write('(FinalGridSpacingInPhysicalUnits %d)' % spacing + '\n')
    f.write('(NumberOfResolutions 4)' + '\n')
    f.write('(MaximumNumberOfIterations 2000)' + '\n')
    f.write('(NumberOfSpatialSamples 2000)' + '\n')
    f.write('(NewSamplesEveryIteration "true")' + '\n')
    f.write('(ImageSampler "Random")' + '\n')
    f.write('(BSplineInterpolationOrder 1)' + '\n')
    f.write('(FinalBSplineInterpolationOrder 3)' + '\n')
    f.write('(DefaultPixelValue 0)' + '\n')
    f.write('(WriteResultImage "false")' + '\n')
    f.close()
    
    # Use registration to get the inverse transformation
    run_executable(type = "elastix", fix = fix_img_name, mov = fix_img_name, outDir = "", para = ["tmp_para.txt"], tp = file_name, mask = False, init = True)
    
    # Return the transformation name
    return "TransformParameters.0.txt"
