# -*- coding: utf-8 -*-
"""
Created on 2014-02-20

@author: Hengkai Guo
"""

from MIRVAP.Core.ScriptBase import ScriptBase

# Input one image(After registration), output nothing but some information
class AnalysisBase(ScriptBase):
    def __init__(self, gui):
        super(AnalysisBase, self).__init__(gui)
        
    def run(self, *args, **kwargs):
        # TO BE DONE
        pass
            
    def analysis(self, data):
        raise NotImplementedError('Method "analysis" Not Impletemented!')
