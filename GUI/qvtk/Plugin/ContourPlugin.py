# -*- coding: utf-8 -*-
"""
Created on 2014-02-16

@author: Hengkai Guo
"""

from MIRVAP.GUI.qvtk.PluginBase import PluginBase
import vtk
import numpy as npy

class ContourPlugin(PluginBase):
    '''
        Click left button:    Add the point in the active contour
        Move left button:     Move the point on the active contour 
        
        Press C Key:          Show or not show the active contour
        Press S Key:          Sort the points on the active contour
        Press Escape Key:     Delete all the points on the active contour
        Press Delete Key:     Delete the active point
        Press Left/Right Key: Slice through the image (Automatic copy points from last slice if empty and controll key pressed)
        Press 1/2/3 Key:      Change 1/2/3 contour into active state
    '''
    def __init__(self):
        super(ContourPlugin, self).__init__()
        self.editable = True
        self.key = 'Contour'
    
    def enable(self, parent, key = 'result', color = ((1, 0, 0), (0, 1, 0), (0, 0, 1)), dash = False, show = True):
        self.parent = parent
        self.datakey = key
        self.contourRep = []
        self.contourWidget = []
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
            
        self.contourRep[0].GetLinesProperty().SetColor(color[0])
        self.contourRep[1].GetLinesProperty().SetColor(color[1])
        self.contourRep[2].GetLinesProperty().SetColor(color[2])
        self.contourRep[0].GetProperty().SetColor(color[0])
        self.contourRep[1].GetProperty().SetColor(color[1])
        self.contourRep[2].GetProperty().SetColor(color[2])
        if self.editable or self.key == 'Centerline':
            self.contourRep[0].GetProperty().SetOpacity(1)
            self.contourRep[1].GetProperty().SetOpacity(1)
            self.contourRep[2].GetProperty().SetOpacity(1)
        else:
            self.contourRep[0].GetProperty().SetOpacity(0)
            self.contourRep[1].GetProperty().SetOpacity(0)
            self.contourRep[2].GetProperty().SetOpacity(0)
        self.contourRep[0].GetActiveProperty().SetColor(1, 1, 1)
        self.contourRep[1].GetActiveProperty().SetColor(1, 1, 1)
        self.contourRep[2].GetActiveProperty().SetColor(1, 1, 1)
        if dash:
            for contourRep in self.contourRep:
                contourRep.GetLinesProperty().SetLineStipplePattern(0xf0f0)
        
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
        
        self.show = show
        self.updateAfter(self.parent.view, int(status[1]))
            
    def disable(self):
        for i in range(3):
            self.contourWidget[i].SetEnabled(0)
            
    def loadCurrentSlicePoint(self, view, slice, *arg):
        # Hint: the position of the point been moved is not integer (To be done)
        point_array = self.parent.parent.getData(self.datakey).pointSet.getSlicePoint(self.key, view, slice - 1)
        if len(arg) and self.editable:
            if not point_array[self.currentContour].shape[0]:
                point_array[self.currentContour] = self.parent.parent.getData(self.datakey).pointSet.getSlicePoint(self.key, view, slice - 1 + arg[0])[self.currentContour]
        result = False
        
        for i in range(3):
            self.contourRep[i].ClearAllNodes()
            if point_array[i].shape[0]:
                result = True
                
                if point_array[i].shape[0] >= 4:
                    
                    # Sort the pointSet for a convex contour
                    point = npy.delete(point_array[i], self.parent.view, axis = 1)
                    core = point.mean(axis = 0)
                    point -= core
                    angle = npy.arctan2(point[:, 1], point[:, 0])
                    ind = angle.argsort()
                    point_array[i][:, :] = point_array[i][ind, :]
                
                for row in point_array[i]:
                    space = self.parent.space
                    if len(space) == 2:
                        space += [1]
                    point = (row * space).tolist()
                    if self.parent.dimension:
                        self.contourRep[i].AddNodeAtWorldPosition(point[0], point[1], 0)
                    else:
                        point[view] = (slice - 1) * space[view]
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
        space = self.parent.space
        #print 'save'
        if len(space) == 2:
            space += [1]
        for i in range(3):
            point_array = self.getAllPoint(i) / space
            # Sort the pointSet for a convex contour
            if point_array.shape[0] >= 4:
                point = npy.delete(point_array, self.parent.view, axis = 1)
                core = point.mean(axis = 0)
                point -= core
                angle = npy.arctan2(point[:, 1], point[:, 0])
                point_array = point_array[angle.argsort()]
            #print i, point_array
            self.parent.parent.getData(self.datakey).pointSet.setSlicePoint(self.key, point_array, view, slice - 1, i)
        #print self.parent.parent.getData(self.datakey).pointSet.data
    def getAllPoint(self, cnt = -1):
        if cnt == -1:
            cnt = self.currentContour
        n = self.contourRep[cnt].GetNumberOfNodes()
        point_array = npy.empty([n, 3], dtype = float)
        l = [0, 0, 0]
        for i in range(n):
            self.contourRep[cnt].GetNthNodeWorldPosition(i, l)
            point_array[i, :] = l
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
            self.parent.window_interactor.GetPicker().Pick(pos[0], pos[1], 0, self.parent.renderer)
            picker = self.parent.window_interactor.GetPicker().GetPickPosition()
            
            if self.key == 'Centerline' or self.contourWidget[self.currentContour].GetWidgetState() == 1:
                self.contourRep[self.currentContour].ClearAllNodes()
            self.contourRep[self.currentContour].AddNodeAtWorldPosition(picker)
            self.contourWidget[self.currentContour].SetWidgetState(2)
            self.contourWidget[self.currentContour].ProcessEventsOn()
            self.contourRep[self.currentContour].ClosedLoopOn()
            
            self.leftMove = False
            self.leftClicked = False
    def KeyPressCallback(self, obj, event):
        ch = self.parent.window_interactor.GetKeySym()
        if ch == 'Return':
            return
        if ch in ['v', 'V']:
            if self.key == 'Contour':
                self.key = 'Centerline'
            else:
                self.key = 'Contour'
            if self.editable or self.key == 'Centerline':
                self.contourRep[0].GetProperty().SetOpacity(1)
                self.contourRep[1].GetProperty().SetOpacity(1)
                self.contourRep[2].GetProperty().SetOpacity(1)
            else:
                self.contourRep[0].GetProperty().SetOpacity(0)
                self.contourRep[1].GetProperty().SetOpacity(0)
                self.contourRep[2].GetProperty().SetOpacity(0)
            self.parent.updateAfter()
            self.parent.render_window.Render()
            return
        if not self.editable:
            return
        if ch == 'Escape':
            self.contourRep[self.currentContour].ClearAllNodes()
            self.contourWidget[self.currentContour].ProcessEventsOff()
            self.contourWidget[self.currentContour].SetWidgetState(1)
            self.parent.render_window.Render()
        if ch == 'c':
            if self.key == 'Centerline':
                return
            if self.contour[self.currentContour]:
                self.contourRep[self.currentContour].GetLinesProperty().SetOpacity(0)
            else:
                self.contourRep[self.currentContour].GetLinesProperty().SetOpacity(1)
            self.contour[self.currentContour] = not self.contour[self.currentContour]
            self.parent.render_window.Render()
            return
        if ch == 's':
            if self.key == 'Centerline':
                return
            point_array = self.getAllPoint()
            if point_array.shape[0] < 4:
                return
            # Sort the pointSet for a convex contour
            point = npy.delete(point_array, self.parent.view, axis = 1)
            core = point.mean(axis = 0)
            point -= core
            angle = npy.arctan2(point[:, 1], point[:, 0])
            ind = angle.argsort()
            for i in range(point_array.shape[0]):
                self.contourRep[self.currentContour].SetNthNodeWorldPosition(i, point_array[ind[i], :].tolist())
            self.parent.render_window.Render()
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
            show = self.parent.parent.gui.getMessageOnStatusBar().replace(oldMessage, newMessage)
            self.parent.parent.gui.showMessageOnStatusBar(show)
        
    def LeftButtonPressCallback(self, obj, event):
        if not self.editable:
            return
        self.leftMove = False
        self.leftClicked = True
    def getNewMessage(self):
        if self.editable:
            return "     %s: " % self.key + self.contourInfo[self.currentContour]
        else:
            return ""
    def updateAfter(self, view, slice, *arg):
        self.loadCurrentSlicePoint(view, slice, *arg)
        if self.show:
            super(ContourPlugin, self).updateAfter(view, slice, *arg)
            newMessage = self.getNewMessage()
            self.parent.parent.gui.showMessageOnStatusBar(self.parent.parent.gui.getMessageOnStatusBar() + newMessage)
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
