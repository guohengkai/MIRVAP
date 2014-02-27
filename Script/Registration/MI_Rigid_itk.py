# -*- coding: utf-8 -*-
"""
Created on 2014-02-07

@author: Hengkai Guo
"""

from MIRVAP.Core.RegistrationBase import RegistrationBase
import MIRVAP.Core.DataBase as db
import itk

class MI_Rigid_itk(RegistrationBase):
    def __init__(self, gui):
        super(MI_Rigid_itk, self).__init__(gui)
    def getName(self):
        return 'Rigid register with MI'
                                 
    def register(self, fixedData, movingData):
        def iterationUpdate():
            currentParameter = transform.GetParameters()
            print "M: %f   P: %f %f %f %f %f " % (optimizer.GetValue(),
            currentParameter.GetElement(0), currentParameter.GetElement(1),
            currentParameter.GetElement(2), currentParameter.GetElement(3),
            currentParameter.GetElement(4))
        image_type = fixedData.getITKImageType()
        fixedImage = fixedData.getITKImage()
        movingImage = movingData.getITKImage()
        dimension = fixedData.getDimension()
        
        registration = itk.ImageRegistrationMethod[image_type, image_type].New()
        imageMetric = itk.MattesMutualInformationImageToImageMetric[image_type, image_type].New()
        if dimension == 2:
            transform = itk.CenteredRigid2DTransform.New()
        elif dimension == 3:
            pass
        optimizer = itk.PowellOptimizer.New()
        interpolator = itk.LinearInterpolateImageFunction[image_type, itk.D].New()
        
        registration.SetOptimizer(optimizer)
        registration.SetTransform(transform)
        registration.SetInterpolator(interpolator)
        registration.SetMetric(imageMetric)
        registration.SetFixedImage(fixedImage)
        registration.SetMovingImage(movingImage)
        registration.SetFixedImageRegion(fixedImage.GetBufferedRegion())
        
        transform.SetAngle(0.0);
        
        # center of the fixed image
        fixedSpacing = fixedImage.GetSpacing()
        fixedOrigin = fixedImage.GetOrigin()
        fixedSize = fixedImage.GetLargestPossibleRegion().GetSize()
        
        centerFixed = (fixedOrigin.GetElement(0) + fixedSpacing.GetElement(0) * fixedSize.GetElement(0) / 2.0,
                       fixedOrigin.GetElement(1) + fixedSpacing.GetElement(1) * fixedSize.GetElement(1) / 2.0)
        
        # center of the moving image 
        movingSpacing = movingImage.GetSpacing()
        movingOrigin = movingImage.GetOrigin()
        movingSize = movingImage.GetLargestPossibleRegion().GetSize()
        
        centerMoving = (movingOrigin.GetElement(0) + movingSpacing.GetElement(0) * movingSize.GetElement(0) / 2.0,
                        movingOrigin.GetElement(1) + movingSpacing.GetElement(1) * movingSize.GetElement(1) / 2.0)
        
        # transform center
        center = transform.GetCenter()
        center.SetElement(0, centerFixed[0])
        center.SetElement(1, centerFixed[1])
        
        # transform translation
        translation = transform.GetTranslation()
        translation.SetElement(0, centerMoving[0] - centerFixed[0])
        translation.SetElement(1, centerMoving[1] - centerFixed[1])
        
        initialParameters = transform.GetParameters()
        
        print "Initial Parameters: "
        print "Angle: %f" % (initialParameters.GetElement(0))
        print "Center: %f, %f" % (initialParameters.GetElement(1), initialParameters.GetElement(2))
        print "Translation: %f, %f" % (initialParameters.GetElement(3), initialParameters.GetElement(4))
        
        registration.SetInitialTransformParameters(initialParameters)

        # optimizer scale
        translationScale = 1.0 / 1000.0
        
        optimizerScales = itk.Array[itk.D](transform.GetNumberOfParameters())
        optimizerScales.SetElement(0, 1.0)
        optimizerScales.SetElement(1, translationScale)
        optimizerScales.SetElement(2, translationScale)
        optimizerScales.SetElement(3, translationScale)
        optimizerScales.SetElement(4, translationScale)
        
        optimizer.SetScales(optimizerScales)
        optimizer.SetStepLength(0.1)
        optimizer.SetMaximumIteration(200)
        
        iterationCommand = itk.PyCommand.New()
        iterationCommand.SetCommandCallable(iterationUpdate)
        optimizer.AddObserver(itk.IterationEvent(), iterationCommand)
        
        # Start the registration process
        registration.Update()
        
        # Get the final parameters of the transformation
        finalParameters = registration.GetLastTransformParameters()
        
        print "Final Registration Parameters "
        print "Angle in radians  = %f" % finalParameters.GetElement(0)
        print "Rotation Center X = %f" % finalParameters.GetElement(1)
        print "Rotation Center Y = %f" % finalParameters.GetElement(2)
        print "Translation in  X = %f" % finalParameters.GetElement(3)
        print "Translation in  Y = %f" % finalParameters.GetElement(4)
        
        # Use the final transform for resampling the moving image.
        resampler = itk.ResampleImageFilter[image_type, image_type].New()
        
        resampler.SetTransform(transform)
        resampler.SetInput(movingImage)
        
        region = fixedImage.GetLargestPossibleRegion()
        
        resampler.SetSize(region.GetSize())
        resampler.SetOutputSpacing(fixedImage.GetSpacing())
        resampler.SetOutputDirection(fixedImage.GetDirection())
        resampler.SetOutputOrigin(fixedImage.GetOrigin())
        resampler.SetDefaultPixelValue(100)
        
        # Cast for output
        outputCast = itk.RescaleIntensityImageFilter[image_type, image_type].New()
        outputCast.SetInput(resampler.GetOutput())
        outputCast.SetOutputMinimum(0)
        outputCast.SetOutputMaximum(255)
        outputCast.Update()
        
        outputImage = outputCast.GetOutput()
        resultData = db.ResultData()
        resultData.setDataFromITKImage(outputImage, image_type)
        return resultData
