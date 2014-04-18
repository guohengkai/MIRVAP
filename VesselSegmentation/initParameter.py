# -*- coding: utf-8 -*-
"""
Created on 2014-04-16

@author: Hengkai Guo
"""

from dict4ini import DictIni
from numpy.random import permutation
import os

def initParameter(ini):
    '''
    This function is to generate a full ini file.
    The format of ini file: ('segment.ini')
        [file]
        datadir = ...
        savedir = ...
        [parameter]
        repeat = ...
    '''
    if not os.path.exists(ini.file.savedir):
        os.mkdir(ini.file.savedir)
    namelist = os.listdir(ini.file.datadir)
    #print namelist
    ini.file.names = namelist

    repeat_time = ini.parameter.repeat
    cnt = len(namelist)
    ini.parameter.sequence = []
    for i in range(repeat_time):
        ini.parameter.sequence += permutation(cnt).tolist()
    #print ini.parameter.sequence

    ini.parameter.current = 0
    ini.save()
    
    return namelist, repeat_time
if __name__ == "__main__":
    ini = DictIni('segment.ini')
    initParameter(ini)
