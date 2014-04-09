# -*- coding: utf-8 -*-
"""
Created on 2014-02-20

@author: Hengkai Guo
"""

from MIRVAP.Core.ScriptBase import ScriptBase

# Input one data(After registration), output nothing but some information
class AnalysisBase(ScriptBase):
    def __init__(self, gui):
        super(AnalysisBase, self).__init__(gui)
        
    def run(self, window):
        window.save()
        data = window.getData()
        self.analysis(data)
            
    def analysis(self, data):
        raise NotImplementedError('Method "analysis" Not Impletemented!')
