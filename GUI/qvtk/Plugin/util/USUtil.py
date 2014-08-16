# -*- coding: utf-8 -*-
"""
Created on 2014-08-10

@author: Hengkai Guo
"""

import cv
import numpy as npy
import scipy.ndimage.filters as flt

def getThreshold(image, center, d, res, sigmaMin):
    temp = image[npy.ceil(center[0] - d / res[0]) : npy.floor(center[0] + d / res[0]), npy.ceil(center[1] - d / res[1]) : npy.floor(center[1] + d / res[1])]
    mu = npy.mean(temp)
    sigma = npy.min([npy.std(temp), sigmaMin])
    return mu + 2.5 * sigma
def getGradientThresholdAndImage(image, center, d, res):
    gradient_img = flt.gaussian_gradient_magnitude(image, 1)
    th = npy.max(gradient_img[npy.ceil(center[0] - d / res[0]) : npy.floor(center[0] + d / res[0]), npy.ceil(center[1] - d / res[1]) : npy.floor(center[1] + d / res[1])])
    return th * 0.75, gradient_img
def isPointValid(x, y, image, th):
    h, w = image.shape
    if x < 0 or x >= h or y < 0 or y >= w:
        return False
    return image[x, y] < th
def getRayPoints(image, center, n, th):
    resultPoints = npy.empty([n, 2], dtype = npy.float32)
    distance = npy.empty([n], dtype = npy.float32)
    angle_list = npy.arange(0, 2 * npy.pi, 2 * npy.pi / n)
    tcos = npy.cos(angle_list)
    tsin = npy.sin(angle_list)

    for i in range(n):
        td = 1
        while isPointValid(npy.round(center[0] + td * tcos[i]), npy.round(center[1] + td * tsin[i]), image, th):
            td += 1
        td -= 1
        resultPoints[i, :] = [npy.round(center[0] + td * tcos[i]), npy.round(center[1] + td * tsin[i])]
        distance[i] = td
    
    return (resultPoints, distance)
def finePrune(points, distance, center, diameter, angle, h, w):
    n = points.shape[0]
    angle_list = npy.arange(0, 2 * npy.pi, 2 * npy.pi / n)
    ellipse_radius = npy.hypot(diameter[0] / 2 * npy.cos(angle_list - angle), 
                   diameter[1] / 2 * npy.sin(angle_list - angle))
                   
    index = npy.where((distance > ellipse_radius) & 
            (0 < points[:, 0]) & (points[:, 0] < h - 1) & 
            (0 < points[:, 1]) & (points[:, 1] < w - 1))
    delta = distance[index] - ellipse_radius[index]
    mu = npy.mean(delta)
    sigma = npy.std(delta)
    
    index = npy.where(distance <= ellipse_radius)
    delta = ellipse_radius[index] - distance[index]
    mu2 = npy.mean(delta)
    sigma2 = npy.std(delta)
    
    index = npy.where((distance > ellipse_radius + mu + 0.05 * sigma) | 
                      (distance < ellipse_radius - mu2 - 0.05 * sigma2) | 
                      (points[:, 0] >= h - 1) | (points[:, 0] <= 0) | 
                      (points[:, 1] >= w - 1) | (points[:, 1] <= 0))
    xx = diameter[0] / 2 * npy.cos(angle_list[index] - angle)
    yy = diameter[1] / 2 * npy.sin(angle_list[index] - angle)
    resultPoints = points
    resultPoints[index, 0] = xx * npy.cos(angle) - yy * npy.sin(angle) + center[0]
    resultPoints[index, 1] = xx * npy.sin(angle) + yy * npy.cos(angle) + center[1]
    return resultPoints
def getPointsFromEllipse(center, diameter, angle, n):
    angle_list = npy.arange(0, 2 * npy.pi, 2 * npy.pi / n)
    xx = diameter[0] * npy.cos(angle_list) / 2
    yy = diameter[1] * npy.sin(angle_list) / 2
    temp_array = npy.empty([n, 2], dtype = npy.float32)
    temp_array[:, 0] = xx * npy.cos(angle) - yy * npy.sin(angle) + center[0]
    temp_array[:, 1] = xx * npy.sin(angle) + yy * npy.cos(angle) + center[1]
    return temp_array
def ellipseFitting(points):
    PointArray2D32f = cv.CreateMat(1, points.shape[0], cv.CV_32FC2)
    for i in range(points.shape[0]):
        PointArray2D32f[0, i] = (points[i, 0], points[i, 1])
    center, diameter, angle = cv.FitEllipse2(PointArray2D32f)
    angle /= 180 * npy.pi
    return (center, diameter, angle)
    
class EllipseLeastSquaresModel:
    def fit(self, data):
        center, diameter, angle = ellipseFitting(data)
        return (center, diameter, angle)
    def get_error(self, data, model):
        (center, diameter, angle) = model
        dis = npy.hypot(data[:, 0] - center[0], data[:, 1] - center[1])
        theta = npy.arctan2(data[:, 1] - center[1], data[:, 0] - center[0]) - angle
        ellipse_radius = npy.hypot(diameter[0] / 2 * npy.cos(theta), 
                   diameter[1] / 2 * npy.sin(theta))
        return npy.abs(dis - ellipse_radius)
        
def ransac(data, model, n, k, t, d):
    # fit model parameters to data using the RANSAC algorithm
    iterations = 0
    bestfit = None
    besterr = npy.inf
    best_inlier_idxs = None
    while iterations < k:
        maybe_idxs, test_idxs = random_partition(n, data.shape[0])
        maybeinliers = data[maybe_idxs, :]
        test_points = data[test_idxs, :]
        maybemodel = model.fit(maybeinliers)
        test_err = model.get_error(test_points, maybemodel)
        
        also_idxs = test_idxs[test_err < t] # select indices of rows with accepted points
        alsoinliers = data[also_idxs, :]
        
        if len(alsoinliers) > d:
            betterdata = npy.concatenate((maybeinliers, alsoinliers))
            bettermodel = model.fit(betterdata)
            better_errs = model.get_error(betterdata, bettermodel)
            thiserr = npy.mean(better_errs)
            if thiserr < besterr:
                bestfit = bettermodel
                besterr = thiserr
                best_inlier_idxs = npy.concatenate((maybe_idxs, also_idxs))
        iterations += 1
    if bestfit is None:
        return -1, -1, -1
    
    return bestfit

def random_partition(n, n_data):
    """return n random rows of data (and also the other len(data)-n rows)"""
    all_idxs = npy.arange(n_data)
    npy.random.shuffle(all_idxs)
    idxs1 = all_idxs[:n]
    idxs2 = all_idxs[n:]
    return idxs1, idxs2
