# -*- coding: utf-8 -*-
"""
Created on 2014-08-10

@author: Hengkai Guo
"""
import numpy as npy

def getCropImageFromCenter(image, d, res, center):
    return image[npy.ceil(center[1] - d / res[1]) : npy.floor(center[1] + d / res[1]), npy.ceil(center[0] - d / res[0]) : npy.floor(center[0] + d / res[0])]
    
def calMinimumCostPathCenterline(center_bottom, center_up1, center_up2, img, img_res):
    # Get the calculation scope of image
    bottom = int(center_bottom[-1] + 0.5)
    top = int(center_up1[-1] + 0.5) + 1
    left = int(npy.max([npy.min([center_bottom[0], center_up1[0], center_up2[0]]) - 10.0 / img_res[0], 0]) + 0.5)
    right = int(npy.min([npy.max([center_bottom[0], center_up1[0], center_up2[0]]) + 10.0 / img_res[0], img.shape[2] - 1]) + 0.5) + 1 # The bound need to be checked
    down = int(npy.max([npy.min([center_bottom[1], center_up1[1], center_up2[1]]) - 10.0 / img_res[1], 0]) + 0.5)
    up = int(npy.min([npy.max([center_bottom[1], center_up1[1], center_up2[1]]) + 10.0 / img_res[1], img.shape[1] - 1]) + 0.5) + 1
    
    current_img = img[bottom : top, down : up, left : right].copy()
    center_bottom -= [bottom, down, up]
    center_up1 -= [bottom, down, up]
    center_up2 -= [bottom, down, up]
    
    # Get medialness of image
    bound
    medial
    
    # Get the intensity thresold from three seed points
    tmp = npy.array(getCropImageFromCenter(current_img, 2.5, img_res, center_bottom).tolist() + \
        getCropImageFromCenter(current_img, 1.5, img_res, center_up1).tolist() + \
        getCropImageFromCenter(current_img, 1.5, img_res, center_up2).tolist())
    mu = npy.mean(tmp)
    sigma = npy.std(tmp)
    
    # Get lumen intensity similarity of image
    similarity = npy.exp(-((current_img - mu) / npy.sqrt(2.0) / sigma) ** 2)
    ind = npy.where(current_img <= mu)
    similarity[ind] = 1
    
    # Get image cost
    alpha = beta = 1
    eps = 1e-6
    
    # Initialize the Dijkstra Algorithm
    
    # Start calculation of minimum cost array
    
    # Get the minimum cost path
    
    return result

def getDirectionGradientTemplate(ux, uy):
    if ux == 0:
        template = npy.array([[uy, uy, uy], [0.0, 0, 0], [-uy, -uy, -uy]])
    elif uy == 0:
        template = npy.array([[-ux, 0.0, ux], [-ux, 0, ux], [-ux, 0, ux]])
    else:
        template = npy.zeros([3, 3], dtype = npy.float32)
        dux = npy.abs(ux)
        duy = npy.abs(uy)
        template[0, 1] = uy * (1 - dux)
        template[1, 2] = ux * (1 - duy)
        if ux * uy > 0:
            template[0, 2] = ux * uy * npy.sign(ux)
            template[2, 0] = -template[0, 2]
            
        else:
            template[0, 0] = ux * uy * npy.sign(uy)
            template[2, 2] = -template[0, 0]
        template[2, 1] = -template[0, 1]
        template[1, 0] = -template[1, 2]
    return template
