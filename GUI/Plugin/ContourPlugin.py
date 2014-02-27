# -*- coding: utf-8 -*-
"""
Created on 2014-02-16

@author: Hengkai Guo
"""

from MIRVAP.Core.PluginBase import PluginBase
import vtk
import numpy as npy

class ContourPlugin(PluginBase):
    '''
        Click left button:    Add the point in the active contour
        Move left button:     Move the point on the active contour 
        
        Press C Key:          Show or not show the active contour
        Press S Key:          Sort the points on the active contour
        Press Delete Key:     Delete the active point
        Press Left/Right Key: Slice through the image (Automatic copy points from last slice if empty)
        Press 1/2/3 Key:      Change 1/2/3 contour into active state
    '''
    def __init__(self):
        super(ContourPlugin, self).__init__()
        self.editable = True
        self.key = 'Contour'
        
    def enable(self, parent):
        self.parent = parent
        self.contourRep = []
        self.contourWidget = []
        print 'enable'
        # The flag of showing the contour
        self.contour = [True, True, True]
        # Avoid putting point when modifying the window level
        self.leftMove = True
        self.leftClicked = False
        
        self.currentContour = 0
        self.contourInfo = ['1 (Red)', '2 (Green)', '3 (Blue)']
        
        for i in range(3):
            self.contourRep.append(vtk.vtkOrientedGlyphContourRepresentation())
            self.contourWidget.append(vtk.vtkContourWidget())
            self.contourWidget[i].SetInteractor(self.parent.window_interactor)
            self.contourWidget[i].SetRepresentation(self.contourRep[i])
            
        self.contourRep[0].GetLinesProperty().SetColor(1, 0, 0)
        self.contourRep[1].GetLinesProperty().SetColor(0, 1, 0)
        self.contourRep[2].GetLinesProperty().SetColor(0, 0, 1)
        self.contourRep[0].GetProperty().SetColor(1, 0, 0)
        self.contourRep[1].GetProperty().SetColor(0, 1, 0)
        self.contourRep[2].GetProperty().SetColor(0, 0, 1)
        self.contourRep[0].GetActiveProperty().SetColor(1, 1, 1)
        self.contourRep[1].GetActiveProperty().SetColor(1, 1, 1)
        self.contourRep[2].GetActiveProperty().SetColor(1, 1, 1)   
        
        for i in range(3):
            eventTranslator = self.contourWidget[i].GetEventTranslator()
            eventTranslator.RemoveTranslation("RightButtonPressEvent")
            eventTranslator.RemoveTranslation("KeyPressEvent")
            eventTranslator.SetTranslation(vtk.vtkCommand.KeyPressEvent, 0, "", 0, "Delete", vtk.vtkWidgetEvent.Delete)
            
            self.contourWidget[i].ProcessEventsOff()
            self.contourWidget[i].SetWidgetState(1)
            self.contourWidget[i].SetEnabled(1)
            self.contourWidget[i].On()
            
        status = self.parent.getDirectionAndSlice()
        self.updateAfter(self.parent.view, int(status[1]))
            
    def disable(self):
        for i in range(3):
            self.contourWidget[i].SetEnabled(0)
            
    def loadCurrentSlicePoint(self, view, slice, last = 0):
#        print '************************************'
#        print 'load'
#        print 'index:', self.parent.index
#        print self.parent.getData().pointSet.data
#        print '************************************'
        # BUG: When open a new data and then open the contour plugin, the pointSet will be the same as the former data
        # And it's difficult to change between data which have contour widgets
        point_array = self.parent.getData().pointSet.getSlicePoint(self.key, view, slice - 1 + last)
#        print '***********************************'
#        print 'load'
#        print point_array
#        print 'index:', self.parent.index
#        print '***********************************'
        result = False
        for i in range(3):
            self.contourRep[i].ClearAllNodes()
            if point_array[i].shape[0]:
                result = True
                for row in point_array[i]:
                    space = self.parent.space
                    if len(space) == 2:
                        space += [1]
                    point = (row * space).tolist()
                    if self.parent.dimension:
                        self.contourRep[i].AddNodeAtWorldPosition(point[0], point[1], 0)
                    else:
                        point[view] = slice - 1
                        self.contourRep[i].AddNodeAtWorldPosition(point)
                self.contourWidget[i].SetWidgetState(2)
                self.contourRep[i].ClosedLoopOn()
                if i == self.currentContour and self.editable:
                    self.contourWidget[self.currentContour].ProcessEventsOn()
            else:
                self.contourWidget[i].ProcessEventsOff()
                self.contourWidget[i].SetWidgetState(1)
        
        self.parent.render_window.Render()
        return result
    def saveCurrentSlicePoint(self, view, slice):
#        print '************************************'
#        print 'save'
#        print 'index:', self.parent.index
#        print self.parent.getData().pointSet.data
#        print '************************************'
        space = self.parent.space
        if len(space) == 2:
            space += [1]
        for i in range(3):
            point_array = self.getAllPoint(i) / space
            # self.parent.getData() == None --> Error
            self.parent.getData().pointSet.setSlicePoint(self.key, point_array, view, slice - 1, i)
#            if i == 0:
#                print '***********************************'
#                print 'save'
#                print point_array
#                print 'index:', self.parent.index
#                print '***********************************'
    def getAllPoint(self, cnt = -1):
        if cnt == -1:
            cnt = self.currentContour
        n = self.contourRep[cnt].GetNumberOfNodes()
        point_array = npy.empty([n, 3], dtype = float)
        l = [0, 0, 0]
        for i in range(n):
            self.contourRep[cnt].GetNthNodeWorldPosition(i, l)
            point_array[i, :] = l
        '''
        if self.parent.dimension:
            point_array = point_array[:, :-1]
        '''
        return point_array
    def MouseMoveCallback(self, obj, event):
        if not self.editable:
            return
        if self.leftClicked:
            self.leftMove = True
    def LeftButtonReleaseCallback(self, obj, event):
        if not self.editable:
            return
        if not self.leftMove:
            pos = self.parent.window_interactor.GetEventPosition()
            self.parent.window_interactor.GetPicker().Pick(pos[0], pos[1], 0, self.parent.window_interactor.GetRenderWindow().GetRenderers().GetFirstRenderer())
            picker = self.parent.window_interactor.GetPicker().GetPickPosition()
            
            if self.key == 'Center' or self.contourWidget[self.currentContour].GetWidgetState() == 1:
                self.contourRep[self.currentContour].ClearAllNodes()
            self.contourRep[self.currentContour].AddNodeAtWorldPosition(picker)
            self.contourWidget[self.currentContour].SetWidgetState(2)
            self.contourWidget[self.currentContour].ProcessEventsOn()
            self.contourRep[self.currentContour].ClosedLoopOn()
            
            self.leftMove = False
            self.leftClicked = False
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'c':
            if self.key == 'Center':
                return
            if self.contour[self.currentContour]:
                self.contourRep[self.currentContour].GetLinesProperty().SetOpacity(0)
            else:
                self.contourRep[self.currentContour].GetLinesProperty().SetOpacity(1)
            self.contour[self.currentContour] = not self.contour[self.currentContour]
            self.parent.render_window.Render()
            return
        if ch == 's':
            if self.key == 'Center':
                return
            point_array = self.getAllPoint()
            if point_array.shape[0] < 4:
                return
            point = npy.delete(point_array, self.parent.view, axis = 1)
            core = point.mean(axis = 0)
            point -= core
            angle = npy.arctan2(point[:, 1], point[:, 0])
            ind = angle.argsort()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].SetNthNodeWorldPosition(i, point_array[ind[i], :].tolist())
            self.parent.render_window.Render()
            return
        if not self.editable:
            return
        if ch in ['1', '2', '3']:
            temp = int(ch) - 1
            if temp == self.currentContour:
                return
            oldMessage = self.getNewMessage()
            if self.contourRep[temp].GetNumberOfNodes() > 0:
                self.contourWidget[temp].ProcessEventsOn()
            self.contourWidget[self.currentContour].ProcessEventsOff()
            self.currentContour = temp
            newMessage = self.getNewMessage()
            show = self.parent.gui.getMessageOnStatusBar().replace(oldMessage, newMessage)
            self.parent.gui.showMessageOnStatusBar(show)
        
    def LeftButtonPressCallback(self, obj, event):
        if not self.editable:
            return
        self.leftMove = False
        self.leftClicked = True
    def getNewMessage(self):
        return "     %s: " % self.key + self.contourInfo[self.currentContour]
    def updateAfter(self, view, slice, *arg):
        if len(arg):
            if not self.loadCurrentSlicePoint(view, slice):
                if self.editable:
                    self.loadCurrentSlicePoint(view, slice, arg[0])
        else:
            self.loadCurrentSlicePoint(view, slice)
        if self.editable:
            newMessage = self.getNewMessage()
            self.parent.gui.showMessageOnStatusBar(self.parent.gui.getMessageOnStatusBar() + newMessage)
    def updateBefore(self, view, slice, *arg):
        if self.editable:
            self.saveCurrentSlicePoint(view, slice)
    def save(self):
        status = self.parent.getDirectionAndSlice()
        self.updateBefore(self.parent.view, int(status[1]))
    def getName(self):
        if self.editable:
            return '%s Editor' % self.key
        else:
            return '%s Viewer' % self.key
