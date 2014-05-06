# -*- coding: utf-8 -*-
"""
Created on 2014-05-01

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import numpy as npy
import numpy.matlib as ml
import itk, vtk
import SimpleITK as sitk

class MRimageRegistration(RegistrationBase):
    def __init__(self, gui):
        super(MRimageRegistration, self).__init__(gui)
    def getName(self):
        return 'MR Images Registration With MI'
                                 
    def register(self, fixedData, movingData):
        clip1 = movingData.info.getData('clip')
        clip2 = fixedData.info.getData('clip')
        
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        
        def iterationUpdate():
            currentParameter = transform.GetParameters()
            print "M: %f   P: %f %f %f" % (optimizer.GetValue(),
            currentParameter.GetElement(0), currentParameter.GetElement(1),
            currentParameter.GetElement(2))
        
        image_type = fixedData.getITKImageType()
        fixedImage = fixedData.getITKImage()
        movingImage = movingData.getITKImage()
        rescale_filter_fixed = itk.RescaleIntensityImageFilter[image_type, image_type].New()
        rescale_filter_fixed.SetInput(fixedImage)
        rescale_filter_fixed.SetOutputMinimum(0)
        rescale_filter_fixed.SetOutputMaximum(255)
        rescale_filter_moving = itk.RescaleIntensityImageFilter[image_type, image_type].New()
        rescale_filter_moving.SetInput(movingImage)
        rescale_filter_moving.SetOutputMinimum(0)
        rescale_filter_moving.SetOutputMaximum(255)
        
        registration = itk.ImageRegistrationMethod[image_type, image_type].New()
        imageMetric = itk.MattesMutualInformationImageToImageMetric[image_type, image_type].New()
        transform = itk.TranslationTransform.New()
        optimizer = itk.RegularStepGradientDescentOptimizer.New()
        interpolator = itk.LinearInterpolateImageFunction[image_type, itk.D].New()
        
        registration.SetOptimizer(optimizer)
        registration.SetTransform(transform)
        registration.SetInterpolator(interpolator)
        registration.SetMetric(imageMetric)
        registration.SetFixedImage(rescale_filter_fixed.GetOutput())
        registration.SetMovingImage(rescale_filter_moving.GetOutput())
        registration.SetFixedImageRegion(fixedImage.GetBufferedRegion())
        
        para = [-clip1[4] * moving_res[0] + clip2[4] * fixed_res[0], -clip1[2] * moving_res[1] + clip2[2] * fixed_res[1], 0]
        transform.SetParameters(para)
        
        initialParameters = transform.GetParameters()
        print "Initial Registration Parameters "
        print initialParameters.GetElement(0)
        print initialParameters.GetElement(1)
        print initialParameters.GetElement(2)
        registration.SetInitialTransformParameters(initialParameters)

        # optimizer scale
        optimizerScales = itk.Array[itk.D](transform.GetNumberOfParameters())
        optimizerScales.SetElement(0, 1.0)
        optimizerScales.SetElement(1, 1.0)
        optimizerScales.SetElement(2, 1.0)
        
        #imageMetric.UseAllPixelsOn()
        imageMetric.SetNumberOfHistogramBins(64)
        imageMetric.SetNumberOfSpatialSamples(800000)
        
        optimizer.MinimizeOn()
        optimizer.SetMaximumStepLength(2.00)
        optimizer.SetMinimumStepLength(0.001)
        optimizer.SetRelaxationFactor(0.8)
        optimizer.SetNumberOfIterations(200)
        
        iterationCommand = itk.PyCommand.New()
        iterationCommand.SetCommandCallable(iterationUpdate)
        optimizer.AddObserver(itk.IterationEvent(), iterationCommand)
        
        # Start the registration process
        try:
            registration.Update()
        except Exception:
            print "error"
            transform.SetParameters([0.0, 0.0, 0.0])
            
        # Get the final parameters of the transformation
        finalParameters = registration.GetLastTransformParameters()
        
        print "Final Registration Parameters "
        print finalParameters.GetElement(0)
        print finalParameters.GetElement(1)
        print finalParameters.GetElement(2)
        
        # Use the final transform for resampling the moving image.
        parameters = transform.GetParameters()
        
        # Fail to use ResampleImageFilter
        x = parameters.GetElement(0)
        y = parameters.GetElement(1)
        z = parameters.GetElement(2)
        T = ml.mat([x, y, z]).T
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = [1, 0, 0, 0, 1, 0, 0, 0, 1] + T.T.tolist()[0]
        transform.SetParameters(para)
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        
        return sitk.GetArrayFromImage(resultImage), {}, para + [0, 0, 0]
