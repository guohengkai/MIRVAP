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
    
    # Get the intensity thresold from three seed points
    tmp = npy.array(getCropImageFromCenter(current_img, 2.5, img_res, center_bottom).tolist() + \
        getCropImageFromCenter(current_img, 1.5, img_res, center_up1).tolist() + \
        getCropImageFromCenter(current_img, 1.5, img_res, center_up2).tolist())
    mu = npy.mean(tmp)
    sigma = npy.std(tmp)
    
    # Get lumen intensity similarity of image
    
    # Get image cost
    alpha = beta = 1
    eps = 1e-6
    
    # Initialize the Dijkstra Algorithm
    
    # Start calculation of minimum cost array
    
    # Get the minimum cost path
    
    return result
