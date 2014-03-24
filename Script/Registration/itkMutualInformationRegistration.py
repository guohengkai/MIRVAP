# -*- coding: utf-8 -*-
"""
Created on 2014-02-07

@author: Hengkai Guo
"""

from MIRVAP.Script.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import itk
import SimpleITK as sitk
import numpy as npy
import numpy.matlib as ml

# Fail to register with MI
class itkMutualInformationRegistration(RegistrationBase):
    def __init__(self, gui):
        super(itkMutualInformationRegistration, self).__init__(gui)
    def getName(self):
        return 'Rigid register with MI'
                                 
    def register(self, fixedData, movingData):
        def iterationUpdate():
            currentParameter = transform.GetParameters()
            print "M: %f   P: %f %f %f %f %f %f" % (optimizer.GetValue(),
            currentParameter.GetElement(0), currentParameter.GetElement(1),
            currentParameter.GetElement(2), currentParameter.GetElement(3),
            currentParameter.GetElement(4), currentParameter.GetElement(5))
        
        image_type = fixedData.getITKImageType()
        fixedImage = fixedData.getITKImage()
        movingImage = movingData.getITKImage()
        dimension = fixedData.getDimension()
        
        registration = itk.ImageRegistrationMethod[image_type, image_type].New()
        imageMetric = itk.MattesMutualInformationImageToImageMetric[image_type, image_type].New()
        if dimension == 2:
            transform = itk.CenteredRigid2DTransform.New()
        elif dimension == 3:
            transform = itk.Euler3DTransform.New()
        optimizer = itk.PowellOptimizer.New()
        interpolator = itk.LinearInterpolateImageFunction[image_type, itk.D].New()
        
        registration.SetOptimizer(optimizer)
        registration.SetTransform(transform)
        registration.SetInterpolator(interpolator)
        registration.SetMetric(imageMetric)
        registration.SetFixedImage(fixedImage)
        registration.SetMovingImage(movingImage)
        registration.SetFixedImageRegion(fixedImage.GetBufferedRegion())
        
        fixed_res = fixedData.getResolution().tolist()
        moving_res = movingData.getResolution().tolist()
        #transform.SetParameters([0.0, 0.0, 0.0, 0.0, 0.0, -329 * fixed_res[-1] + 95 * moving_res[-1]])
        
        initialParameters = transform.GetParameters()
        print "Initial Registration Parameters "
        print initialParameters.GetElement(0)
        print initialParameters.GetElement(1)
        print initialParameters.GetElement(2)
        print initialParameters.GetElement(3)
        print initialParameters.GetElement(4)
        print initialParameters.GetElement(5)
        registration.SetInitialTransformParameters(initialParameters)

        # optimizer scale
        translationScale = 100.0
        
        optimizerScales = itk.Array[itk.D](transform.GetNumberOfParameters())
        optimizerScales.SetElement(0, 1.0)
        optimizerScales.SetElement(1, 1.0)
        optimizerScales.SetElement(2, 1.0)
        optimizerScales.SetElement(3, translationScale)
        optimizerScales.SetElement(4, translationScale)
        optimizerScales.SetElement(5, translationScale)
        
        optimizer.SetScales(optimizerScales)
        optimizer.SetStepLength(0.1)
        optimizer.SetMaximumIteration(200)
        
        iterationCommand = itk.PyCommand.New()
        iterationCommand.SetCommandCallable(iterationUpdate)
        optimizer.AddObserver(itk.IterationEvent(), iterationCommand)
        
        # Start the registration process
        try:
            registration.Update()
        except Exception:
            print "error"
            transform.SetParameters([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            
        # Get the final parameters of the transformation
        finalParameters = registration.GetLastTransformParameters()
        
        print "Final Registration Parameters "
        print finalParameters.GetElement(0)
        print finalParameters.GetElement(1)
        print finalParameters.GetElement(2)
        print finalParameters.GetElement(3)
        print finalParameters.GetElement(4)
        print finalParameters.GetElement(5)
        
        # Use the final transform for resampling the moving image.
        parameters = transform.GetParameters()
        
        # Fail to use ResampleImageFilter
        x = parameters.GetElement(0)
        y = parameters.GetElement(1)
        z = parameters.GetElement(2)
        Xr = ml.mat([[1, 0, 0], [0, npy.cos(x), npy.sin(x)], [0, -npy.sin(x), npy.cos(x)]])
        Yr = ml.mat([[npy.cos(y), 0, -npy.sin(y)], [0, 1, 0], [npy.sin(y), 0, npy.cos(y)]])
        Zr = ml.mat([[npy.cos(z), npy.sin(z), 0], [-npy.sin(z), npy.cos(z), 0], [0, 0, 1]])
        R = Xr * Yr * Zr
        T = ml.mat([parameters.GetElement(3), parameters.GetElement(4), parameters.GetElement(5)]).T
        T = -T
        T = R * T
        transform = sitk.Transform(3, sitk.sitkAffine)
        para = R.reshape(1, -1).tolist()[0] + T.T.tolist()[0]
        transform.SetParameters(para)
        transform.SetFixedParameters([0.0, 0.0, 0.0])
        
        movingImage = movingData.getSimpleITKImage()
        fixedImage = fixedData.getSimpleITKImage()
        resultImage = sitk.Resample(movingImage, fixedImage, transform, sitk.sitkLinear, 0, sitk.sitkFloat32)
        array = sitk.GetArrayFromImage(resultImage)
        print npy.sum(array)
        
        return array, {}, para
