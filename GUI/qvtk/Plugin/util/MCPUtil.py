# -*- coding: utf-8 -*-
"""
Created on 2014-08-10

@author: Hengkai Guo
"""
import numpy as npy
import scipy.ndimage.filters as flt
import scipy.interpolate as itp

def getCropImageFromCenter(image, d, res, center):
    return image[npy.ceil(center[1] - d / res[1]) : npy.floor(center[1] + d / res[1]), npy.ceil(center[0] - d / res[0]) : npy.floor(center[0] + d / res[0])]

def isOutOfBound(point, size):
    for i in range(len(point)):
        if point[i] < 0 or point[i] > size[i] - 1:
            return True
    return False
def isPointEqual(pointx, pointy):
    delta = npy.round(npy.abs(pointx - pointy))
    return delta[0] <= 1e-6 and delta[1] <= 1e-6 and delta[2] <= 1e-6
def getImageDataAt(img, point):
    #if isOutOfBound(point, img.shape):
    #    return 0
        
    x = int(npy.floor(point[0]))
    y = int(npy.floor(point[1]))
    if x == point[0] and y == point[1]:
        return img[x, y]
    r1 = point[0] - x
    r2 = point[1] - y
    if x == point[0]:
        return img[x, y] * (1 - r2) + img[x, y + 1] * r2
    if y == point[1]:
        return img[x, y] * (1 - r1) + img[x + 1, y] * r1
   
    i = img[x, y] * (1 - r1) + img[x + 1, y] * r1
    j = img[x, y + 1] * (1 - r1) + img[x + 1, y + 1] * r1
    return i * (1 - r2) + j * r2
    
def calMinimumCostPathCenterline(center_bottom, center_up1, center_up2, img, img_res):
    # Get the calculation scope of image
    bottom = int(center_bottom[-1] + 0.5)
    top = int(center_up1[-1] + 0.5) + 1
    left = int(npy.max([npy.min([center_bottom[0], center_up1[0], center_up2[0]]) - 10.0 / img_res[0], 0]) + 0.5)
    right = int(npy.min([npy.max([center_bottom[0], center_up1[0], center_up2[0]]) + 10.0 / img_res[0], img.shape[2] - 1]) + 0.5) + 1 # The bound need to be checked
    down = int(npy.max([npy.min([center_bottom[1], center_up1[1], center_up2[1]]) - 10.0 / img_res[1], 0]) + 0.5)
    up = int(npy.min([npy.max([center_bottom[1], center_up1[1], center_up2[1]]) + 10.0 / img_res[1], img.shape[1] - 1]) + 0.5) + 1
    
    current_img = img[bottom : top, down : up, left : right].copy()
    center_bottom -= [left, down, bottom]
    center_up1 -= [left, down, bottom]
    center_up2 -= [left, down, bottom]
    
    # Get medialness of image
    n = 24 # Number of angles
    Rmax = 15
    Rmin = 1
    step = 0.20
    sigma = [0.5, 0.75, 1, 1.25, 1.5]
    medial = npy.zeros(current_img.shape)
    ux = npy.cos(2 * npy.pi * npy.arange(n) / n)
    uy = npy.sin(2 * npy.pi * npy.arange(n) / n)
    
    for z in range(current_img.shape[0]):
        print "Slice %d..." % z
        m = npy.zeros([int((Rmax - Rmin) / step + 1.5), current_img.shape[1], current_img.shape[2]], dtype = npy.float32)
        
        for i in range(n):
            # Get the directional gradient image
            template = getDirectionGradientTemplate(ux[i], uy[i])
            grad_img = npy.zeros([len(sigma), current_img.shape[1], current_img.shape[2]], dtype = npy.float32)
            for j in range(len(sigma)):
                grad_img[j, :, :] = flt.gaussian_filter(current_img[z, :, :], sigma[j])
                grad_img[j, :, :] = flt.convolve(grad_img[j, :, :], template)
            
            # Get the boundary messure along the ray
            ind = npy.argmax(npy.abs(grad_img), axis = 0)
            b = npy.zeros(current_img.shape[1:], dtype = npy.float32)
            for p in range(b.shape[0]):
                for q in range(b.shape[1]):
                    b[p, q] = grad_img[ind[p, q], p, q]
            del grad_img, ind
            
            # Get the normalized edge response of different radius
            print i
            tmp = npy.zeros([m.shape[0]], dtype = npy.float32)
            
            for y0 in range(b.shape[0]):
                for x0 in range(b.shape[1]):
                    min = 0.0
                    for R in npy.arange(step, Rmin, step):
                        x = x0 + ux[i] * R / img_res[0]
                        y = y0 + uy[i] * R / img_res[1]
                        if isOutOfBound([x, y], current_img.shape[:0:-1]):
                            break
                        min = npy.min([getImageDataAt(b, [y, x]), min])
                    x = x0 + ux[i] * Rmin / img_res[0]
                    y = y0 + uy[i] * Rmin / img_res[1]
                    tmp[:] = 0
                    max = 1.0
                    
                    for j in range(m.shape[0]):
                        if isOutOfBound([x, y], current_img.shape[:0:-1]):
                            break
                        tmp[j] = getImageDataAt(b, [y, x])
                        
                        max = npy.max([max, tmp[j]])
                        min = npy.min([min, tmp[j]])
                        tmp[j] = npy.max([tmp[j] + min, 0])
                        
                        x += ux[i] * step / img_res[0]
                        y += uy[i] * step / img_res[1]
                    m[:, y0, x0] += tmp / max
            del b
        medial[z, :, :] = npy.max(m, axis = 0) / n
        del m
    print "Finish medialness calculation!"
    
    # Get the intensity thresold from three seed points
    eps = 1e-6
    tmp = npy.array(getCropImageFromCenter(current_img, 2.5, img_res, center_bottom).flatten().tolist() + \
        getCropImageFromCenter(current_img, 1.5, img_res, center_up1).flatten().tolist() + \
        getCropImageFromCenter(current_img, 1.5, img_res, center_up2).flatten().tolist(), dtype = npy.float32)
    mu = npy.mean(tmp)
    sigma = npy.std(tmp) + eps
    del tmp
    
    # Get lumen intensity similarity of image
    similarity = npy.exp(-((current_img - mu) / npy.sqrt(2.0) / sigma) ** 2)
    ind = npy.where(current_img <= mu)
    similarity[ind] = 1
    print "Finish similarity calculation!"
    
    # Get image cost
    alpha = beta = 1
    cost = 1 / (eps + (medial ** alpha) * (similarity ** beta))
    del medial, similarity
    print "Finish image cost calculation!"
    
    # Initialize the Dijkstra Algorithm
    dis = npy.zeros(cost.shape, dtype = npy.float32)
    dis[:, :, :] = 1e10
    dis[tuple(center_bottom[::-1])] = 0
    visit = npy.ones(cost.shape, dtype = npy.bool)
    delta = npy.zeros([26, 3], dtype = npy.int16)
    dd = npy.zeros(26, dtype = npy.float32)
    p = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            for k in range(-1, 2):
                if i == 0 and j == 0 and k == 0:
                    continue
                delta[p, :] = [i, j, k]
                dd[p] = npy.sqrt(i ** 2 + j ** 2 + k ** 2)
                p += 1
    cnt = 0
    pre = dict()
    
    # Start calculation of minimum cost array
    while cnt < 2:
        # Find the minimum distance point
        ind = [0, 0, 0]
        min = 1e10
        for i in range(dis.shape[0]):
            for j in range(dis.shape[1]):
                for k in range(dis.shape[2]):
                    if not visit[i, j, k]:
                        continue
                    if min > dis[i, j, k]:
                        min = dis[i, j, k]
                        ind[:] = [i, j ,k]
                        
        pos = npy.array(ind)
        ind = tuple(ind)
        if not visit[ind]:
            print "Fail to extract the centerline!"
            return npy.array([[-1, -1, -1.0, -1]])
        visit[ind] = False
        print "%d points remains. " % npy.sum(visit)
        
        # See if successful
        if isPointEqual(pos[::-1], center_up1) or isPointEqual(pos[::-1], center_up2):
            cnt += 1
            print "Find the %d point!" % cnt
            if cnt == 2:
                break
        
        # Update the other distance
        new_dis = dis[ind]
        for i in range(26):
            tmp = pos + delta[i, :]
            if isOutOfBound(tmp, dis.shape):
                continue
            tmp_ind = tuple(tmp)
            if dis[tmp_ind] > new_dis + cost[tmp_ind] * dd[i]:
                dis[tmp_ind] = new_dis + cost[tmp_ind] * dd[i]
                pre[tmp_ind] = ind
    print "Finish Dijkstra algorithm!"
    
    # Get the minimum cost path
    result = npy.array([[-1, -1, -1.0, -1]])
    pos = tuple(npy.round(center_up1[::-1]))
    visit[tuple(center_bottom[::-1])] = True
    while not visit[pos]:
        visit[pos] = True
        result = npy.append(result, [(npy.array(pos[::-1]) + [left, down, bottom]).tolist() + [0]], axis = 0)
        pos = pre[pos]
    result = npy.append(result, [list(pos[::-1]) + [0]], axis = 0)
    pos = tuple(npy.round(center_up2[::-1]))
    while not visit[pos]:
        visit[pos] = True
        result = npy.append(result, [(npy.array(pos[::-1]) + [left, down, bottom]).tolist() + [2]], axis = 0)
        pos = pre[pos]
        
    return result

def getDirectionGradientTemplate(ux, uy):
    if npy.abs(ux) < 1e-6:
        template = npy.array([[uy, uy, uy], [0.0, 0, 0], [-uy, -uy, -uy]])
    elif npy.abs(uy) < 1e-6:
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
            template[0, 0] = ux * uy * npy.sign(ux)
            template[2, 2] = -template[0, 0]
        template[2, 1] = -template[0, 1]
        template[1, 0] = -template[1, 2]
    return template
