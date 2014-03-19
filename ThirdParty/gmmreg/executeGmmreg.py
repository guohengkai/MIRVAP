# -*- coding: utf-8 -*-
"""
Created on 2014-03-19

@author: Hengkai Guo
"""

import sys, os
import subprocess
import ConfigParser
import numpy as npy

def run_executable(gmmreg_exe = None, f_config = "temp.ini", method = "rigid"):
    if gmmreg_exe is None:
        gmmreg_exe = get_exe_path() + "/gmmreg.exe"
    cmd = '%s %s %s' % (gmmreg_exe, f_config, method)
    return subprocess.call(cmd, shell = True)
def initial_data(fixedPoints, movingPoints, methodname = "rigid"):
    path = get_exe_path()
    npy.savetxt("%s/model.txt" % path, movingPoints)
    npy.savetxt("%s/scene.txt" % path, fixedPoints)
    
    wfile = open("%s/temp.ini" % path, 'w')
    wfile.write("[FILES]\n")
    wfile.write("model = %s/model.txt\n" % path)
    wfile.write("scene = %s/scene.txt\n" % path)
    wfile.write("final_%s = %s/final.txt\n" % (methodname, path))
    wfile.write("transformed_model = %s/trans_model.txt\n" % path)
    wfile.write("[GMMREG_OPT]\n")
    wfile.write("normalize = 1\n")
    wfile.write("level = 2\n")
    wfile.write("sigma = .5 .1 .02\n")
    wfile.write("max_function_evals = 10 100 100 200\n")
    wfile.close()
def get_final_result(f_config = "temp.ini", methodname = "rigid"):
    c = ConfigParser.ConfigParser()
    c.read("%s/%s" % (get_exe_path(), f_config))
    section_common = 'FILES'
    pf = c.get(section_common,'final_' + methodname)
    tf = c.get(section_common,'transformed_model')

    trans = npy.loadtxt(tf)
    para = npy.loadtxt(pf)
    return trans, para
def get_exe_path():
    path = sys.argv[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
        
    path += '/ThirdParty/gmmreg'
    #path += '\\gmmreg.exe'
    return path

if __name__ == "__main__":
    initial_data(npy.loadtxt('./face_data/face_Y.txt'), npy.loadtxt('./face_data/face_X.txt'))
    print run_executable(get_exe_path())
    trans, para = get_final_result()
    
