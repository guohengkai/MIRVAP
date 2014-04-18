# -*- coding: utf-8 -*-
"""
Created on 2014-04-17

@author: Hengkai Guo
"""
from distutils.core import setup
import py2exe

py2exe_options = dict(excludes = ['_ssl',  # Exclude _ssl
                                'pyreadline', 'doctest', 'locale', 
                                'optparse', 'calendar', 'pdb', 
                                'inspect', "pywin", "pywin.debugger", 
                                "pywin.debugger.dbgcon", "pywin.dialogs", "pywin.dialogs.list", 
                                "Tkconstants", "Tkinter", "tcl"],  # Exclude standard library
                      includes = ["sip", "PyQt4.QtOpenGL", "vtk.vtkRenderingPythonSIP", 
                                "vtk.vtkCommonPythonSIP", "vtk.vtkFilteringPythonSIP", 
                                "scipy.sparse.csgraph._validation"], 
                      compressed = True,  # Compress library.zip
                      )
setup(windows = ["main2.py", "initParameter.py"], options = {'py2exe': py2exe_options})
