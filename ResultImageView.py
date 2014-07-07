# -*- coding: utf-8 -*-
"""
Created on 2014-03-02

@author: Hengkai Guo
"""

from WidgetViewBase import SingleDataView

class ResultImageView(SingleDataView):
    def __init__(self, parent = None):
        super(ResultImageView, self).__init__(parent)
        self.type = 'any'
    def getName(self):
        return "Main/Result Image View"
