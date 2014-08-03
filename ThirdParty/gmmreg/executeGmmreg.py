# -*- coding: utf-8 -*-
"""
Created on 2014-03-19

@author: Hengkai Guo
"""

import sys, os
import subprocess
import ConfigParser
import numpy as npy

# "rigid" for rigid registration, "EM_TPS" for TPS-RPM algorithm
def run_executable(gmmreg_exe = None, f_config = "temp.ini", method = "rigid"):
    if gmmreg_exe is None:
        gmmreg_exe = get_exe_path() + "/gmmreg.exe"
    if method == 'rigid':
        methodname = 'rigid'
    else:
        methodname = 'EM_TPS'
    cmd = '"%s" "%s" %s' % (gmmreg_exe, get_exe_path() + "/" + f_config, methodname)
    #print cmd
    return subprocess.call(cmd, shell = True)
    
def initial_data(fixedPoints, movingPoints, ctrl_pts = None):
    if ctrl_pts == None:
        ctrl_pts = fixedPoints
    path = get_exe_path()
    npy.savetxt("%s/model.txt" % path, movingPoints)
    npy.savetxt("%s/scene.txt" % path, fixedPoints)
    npy.savetxt("%s/ctrl_pts.txt" % path, ctrl_pts)
    wfile = open("%s/temp.ini" % path, 'w')
    
    # Parameter for file path
    wfile.write("[FILES]\n")
    wfile.write("model = %s/model.txt\n" % path)
    wfile.write("scene = %s/scene.txt\n" % path)
    wfile.write("ctrl_pts = %s/ctrl_pts.txt\n" % path)
    wfile.write("final_rigid = %s/final_rigid.txt\n" % path)
    wfile.write("final_params = %s/final_params.txt\n" % path)
    wfile.write("transformed_model = %s/trans_model.txt\n" % path)
    wfile.write("para = %s/para.txt\n" % path)
    wfile.write("basis_params = %s/basis_params.txt\n" % path)
    
    # Parameter for rigid registration
    wfile.write("[GMMREG_OPT]\n")
    wfile.write("normalize = 1\n")
    wfile.write("level = 2\n")
    wfile.write("sigma = .5 .1\n")
    wfile.write("max_function_evals = 100 200\n")
    
    # Parameter for TPS-RPM algorithm
    wfile.write("[GMMREG_EM]\n")
    wfile.write("normalize = 1\n")
    wfile.write("outliers = 1\n")
    wfile.write("sigma = .5\n")
    wfile.write("beta = 3\n")
    wfile.write("lamda = 1\n")
    wfile.write("anneal = 0.9\n")
    wfile.write("tol = 1e-8\n")
    wfile.write("emtol = 1e-5\n")
    wfile.write("max_iter = 200\n")
    wfile.write("max_em_iter = 20\n")
    
    wfile.close()
    
def get_final_result(f_config = "temp.ini", methodname = "rigid"):
    c = ConfigParser.ConfigParser()
    c.read("%s/%s" % (get_exe_path(), f_config))
    section_common = 'FILES'
    
    if methodname == 'rigid':
        pf = c.get(section_common,'final_rigid')
        tf = c.get(section_common,'transformed_model')
    else:
        pf = c.get(section_common,'final_params')
        tf = c.get(section_common,'basis_params')
    pf2 = c.get(section_common,'para')

    trans = npy.loadtxt(tf) # When non-rigid, it becomes the basis matrix
    para = npy.loadtxt(pf)
    para2 = npy.loadtxt(pf2)
    return trans, para, para2
    
def get_exe_path():
    path = sys.argv[0]
    if os.path.isfile(path):
        path = os.path.dirname(path)
        
    path += '/ThirdParty/gmmreg'
    #print path
    return path
    
def clear_temp_file(f_config = "temp.ini", methodname = "rigid"):
    c = ConfigParser.ConfigParser()
    ini = "%s/%s" % (get_exe_path(), f_config)
    c.read(ini)
    section_common = 'FILES'
    pf = c.get(section_common,'final_' + methodname)
    tf = c.get(section_common,'transformed_model')
    mf = c.get(section_common,'model')
    sf = c.get(section_common,'scene')
    
    try:
        os.remove(pf)
        os.remove(tf)
        os.remove(mf)
        os.remove(sf)
        os.remove(ini)
    except WindowsError:
        pass
