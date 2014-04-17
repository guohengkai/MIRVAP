# -*- coding: utf-8 -*-
"""
Created on 2014-04-17

@author: Hengkai Guo
"""
from distutils.core import setup
import py2exe

py2exe_options = dict(
                      ascii = True,  # Exclude encodings
                      excludes = ['_ssl',  # Exclude _ssl
                                'pyreadline', 'doctest', 'locale', 
                                'optparse', 'pickle', 'calendar', 'pdb', 
                                'inspect', "pywin", "pywin.debugger", 
                                "pywin.debugger.dbgcon", "pywin.dialogs", "pywin.dialogs.list", 
                                "Tkconstants", "Tkinter", "tcl"],  # Exclude standard library
                      compressed = True,  # Compress library.zip
                      )
setup(windows = [{"script": "initParameter.py"}], options = {'py2exe': py2exe_options})
