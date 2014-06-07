# -*- coding: utf-8 -*-
"""
Created on 2014-06-06

@author: Hengkai Guo
"""

import numpy as npy

def po_circle(center, radius, nedges, o_resolution):
    if nedges < 3:
        nedges = round(2 * npy.pi * radius / o_resolution)
        if nedges < 3:
            nedges = 3
    
    sampling_angles = 2 * npy.pi / nedges * npy.arange(nedges, 0, -1)
    
    circle = npy.zeros([2, nedges + 1], dtype = npy.float32)
    circle[0, :-1] = center[0] + radius * npy.cos(sampling_angles)
    circle[1, :-1] = center[1] + radius * npy.sin(sampling_angles)
    circle[:, -1] = circle[:, 0]
    
    return circle
def po_orientation(polygon):
    edges = npy.zeros(polygon.shape)
    lengths = npy.zeros(polygon.shape[1])
    edges[:, :-1] = npy.diff(polygon, 1, 1)
    lengths[:-1] = npy.sqrt(npy.sum(edges[:, :-1] ** 2, 0))
    edges[:, -1] = edges[:, 0]
    lengths[-1] = lengths[0]
    
    cosines = npy.sum(edges[:, :-1] * edges[:, 1:], 0)
    cosines[cosines > 1] = 1
    cosines[cosines < -1] = -1
    angles = npy.arccos(cosines)
    
    determinant = edges[0, :-1] * edges[1, 1:] - edges[1, :-1] * edges[0, 1:]
    
    orientation = npy.sum(npy.sign(determinant) * angles)
    
    return orientation
