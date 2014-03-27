# -*- coding: utf-8 -*-
"""
Created on 2014-03-25

@author: Hengkai Guo
"""

import sys
sys.path.append("E:\\GitHub")

from MIRVAP.Script.Load.LoadDicomFile import LoadDicomFile
import MIRVAP.Core.DataBase as db
import matplotlib.pyplot as plt
import cv2 as cv

ldf = LoadDicomFile(None)
dir = ["E:\\GitHub\\MIRVAP\\Test\\Data\\IM_1649"]
data = ldf.load(dir)[0]
image = data.getData()

plt.imshow(image[100], cmap = cm.gray)
plt.figure()
plt.hist(image[100].ravel(), 256)