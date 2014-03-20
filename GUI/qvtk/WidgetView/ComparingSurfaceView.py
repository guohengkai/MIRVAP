# -*- coding: utf-8 -*-
"""
Created on 2014-03-20

@author: Hengkai Guo
"""
from MIRVAP.GUI.qvtk.WidgetView.SurfaceView import SurfaceView
import vtk
import numpy as npy

class ComparingSurfaceView(SurfaceView):
    def __init__(self, parent = None):
        super(ComparingSurfaceView, self).__init__(parent)
        self.type = 'registration'
    def getName(self):
        return "Comparing Surface View"
    def setWidgetView(self, widget):
        super(ComparingSurfaceView, self).setWidgetView(widget, [[1, 0, 0], [1, 0, 0], [1, 0, 0]])
        
        point_array_fix = self.parent.getData('fix').pointSet
        point_data_fix = npy.array(point_array_fix.getData('Contour'))
        
        if point_data_fix is None or not point_data_fix.shape[0]:
            return
        zmin = int(npy.min(point_data_fix[:, 2]) + 0.5)
        zmax = int(npy.max(point_data_fix[:, 2]) + 0.5)
        
        point_data_fix[:, :2] *= self.spacing[:2]
        
        for cnt in range(3, 6):
            self.contours.append(vtk.vtkPolyData())
            self.delaunay3D.append(vtk.vtkDelaunay3D())
            self.delaunayMapper.append(vtk.vtkDataSetMapper())
            self.surface_actor.append(vtk.vtkActor())
            
            point_fix = point_data_fix[npy.where(npy.round(point_data_fix[:, -1]) == cnt - 3)]
            if not point_fix.shape[0]:
                continue
                
            self.cells = vtk.vtkCellArray()
            self.points = vtk.vtkPoints()
            l = 0
            for i in range(zmin, zmax + 1):
                data = point_fix[npy.where(npy.round(point_fix[:, 2]) == i)]
                if data is not None:
                    if data.shape[0] == 0:
                        continue
                    count = data.shape[0]
                    points = vtk.vtkPoints()
                    for j in range(count):
                        points.InsertPoint(j, data[j, 0], data[j, 1], data[j, 2])
                    
                    para_spline = vtk.vtkParametricSpline()
                    para_spline.SetXSpline(vtk.vtkKochanekSpline())
                    para_spline.SetYSpline(vtk.vtkKochanekSpline())
                    para_spline.SetZSpline(vtk.vtkKochanekSpline())
                    para_spline.SetPoints(points)
                    para_spline.ClosedOn()
                    
                    # The number of output points set to 10 times of input points
                    numberOfOutputPoints = count * 10
                    self.cells.InsertNextCell(numberOfOutputPoints)
                    for k in range(0, numberOfOutputPoints):
                        t = k * 1.0 / numberOfOutputPoints
                        pt = [0.0, 0.0, 0.0]
                        para_spline.Evaluate([t, t, t], pt, [0] * 9)
                        if pt[0] != pt[0]:
                            print pt
                            continue
                        self.points.InsertPoint(l, pt[0], pt[1], pt[2])
                        self.cells.InsertCellPoint(l)
                        l += 1

            self.contours[cnt].SetPoints(self.points)
            self.contours[cnt].SetPolys(self.cells)
            
            self.delaunay3D[cnt].SetInput(self.contours[cnt])
            self.delaunay3D[cnt].SetAlpha(2)
            
            self.delaunayMapper[cnt].SetInput(self.delaunay3D[cnt].GetOutput())
            
            self.surface_actor[cnt].SetMapper(self.delaunayMapper[cnt])
            self.surface_actor[cnt].GetProperty().SetDiffuseColor(0, 0, 1)
            self.surface_actor[cnt].GetProperty().SetSpecularColor(1, 1, 1)
            self.surface_actor[cnt].GetProperty().SetSpecular(0.4)
            self.surface_actor[cnt].GetProperty().SetSpecularPower(50)
            
            self.renderer.AddViewProp(self.surface_actor[cnt])
        
        self.render_window.Render()
