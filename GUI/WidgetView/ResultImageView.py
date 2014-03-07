# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from MIRVAP.Core.WidgetViewBase import SingleDataView

class ResultImageView(SingleDataView):
    def __init__(self, parent = None):
        super(ResultImageView, self).__init__(parent)
    def getName(self):
        return "Main(Result) Image View"
