# -*- coding: utf-8 -*-
"""
Created on 2014-06-06

@author: Hengkai Guo
"""

import numpy as npy
import scipy.interpolate as itp
import scipy.optimize as opt
from mahotas.polygon import fill_polygon
from po_function import po_orientation

class ac_energy(object):
    def start(self, width_of_window = 15, conv_slope = 0.1):
        self.width_of_window = 15
        self.conv_slope = 0.1
        
        self.indices_of_iterations = npy.arange(1, width_of_window + 1)
        self.sum_of_indices = (width_of_window + 1) * width_of_window / 2
        self.sum_of_squared_indices = (2 * width_of_window + 1) * self.sum_of_indices / 3
        self.difference_of_sums = self.sum_of_squared_indices - self.sum_of_indices ** 2 / width_of_window
        
        self.energies = npy.array([])
        self.slopes = npy.array([])
        
    def store(self, energy):
        iteration = len(self.energies)
        self.energies = npy.append(self.energies, energy)
        
        if len(self.energies) >= self.width_of_window:
            recent_energies = self.energies[-self.width_of_window:]
            self.slopes = npy.append(self.slopes, (npy.sum(self.indices_of_iterations * recent_energies) - self.sum_of_indices * npy.sum(recent_energies) / self.width_of_window) / self.difference_of_sums)
            
            if abs(self.slopes[-1]) < self.conv_slope:
                return True
            else:
                noscillations = npy.sum(npy.diff(npy.sign(npy.diff(recent_energies))) != 0)
                avg_energy = npy.mean(recent_energies)
                above_idx = npy.where(recent_energies > avg_energy)
                below_idx = npy.where(recent_energies < avg_energy)
                if (noscillations > 0.8 * self.width_of_window) and (abs(npy.mean(above_idx) - npy.mean(below_idx)) < 0.1 * self.width_of_window):
                    return True
                else:
                    return False
        else:
            self.slopes = npy.append(self.slopes, float('nan'))
            return False
class ac_evolution(object):
    def start(self, amplitude_limit):
        self.is_step_variable = (amplitude_limit <= 0)
        self.mean_amplitudes = npy.array([1.0])
        if self.is_step_variable:
            self.steps = npy.array([-amplitude_limit], dtype = npy.float32)
        
    def store(self, amplitudes, step):
        if self.mean_amplitudes[-1] >= 0:
            self.mean_amplitudes = npy.append(self.mean_amplitudes, -1)
            if self.is_step_variable:
                self.steps = npy.append(self.steps, 0)
        
        self.mean_amplitudes[-1] = npy.mean(npy.abs(amplitudes))
        if self.is_step_variable:
            self.steps[-1] = step
    def step(self):
        if self.is_step_variable:
            return self.steps[1:]
        else:
            return npy.array([])
def ac_flattening(acontour):
    return acontour[:, :-1]
def ac_normal(acontour):
    #sgn = npy.sign(po_orientation(acontour))
    s = acontour.shape[1]
    cnt = npy.arange(0, s)
    spline = [0, 0]
    for i in range(2):
        spline[i] = itp.InterpolatedUnivariateSpline(cnt, acontour[i, :])
    direction = npy.zeros([2, s - 1])
    tangent = [0, 0]
    for j in range(s - 1):
        for i in range(2):
            tangent[i] = spline[i].derivatives(j)[1]
        direction[0, j] = tangent[1]
        direction[1, j] = -tangent[0]
        direction[:, j] /= npy.sqrt(npy.sum(direction[:, j] ** 2))
    return direction
def ac_amplitude(vertices, amplitude, amplitude_limit, framesize, o_acontour = None, \
        o_direction = None, o_previous_steps = None, o_current_energy = None, o_energy_function = None, o_resolution = None, o_context = None):
    def n_optimal_step(amplitude_tmp):
        current_limit = -amplitude_limit
        
        increment_limit = 0.1
        intervals = 5
        allowed_increase = 1.7
        ad_hoc = 5
        
        if o_previous_steps.shape[0] > 0:
            accounting_since = max(1, o_previous_steps.shape[0] - npy.floor(npy.min(framesize) / (ad_hoc * npy.mean(o_previous_steps)))) - 1
            current_limit = min(current_limit, allowed_increase * npy.mean(o_previous_steps[accounting_since:]))
        else:
            accounting_since = 0
        
        increment = max((current_limit - increment_limit) / intervals, increment_limit)
        list_of_steps = npy.arange(increment_limit, current_limit + increment, increment)
        
        energies = npy.zeros(list_of_steps.shape[0] + 1)
        energies[0] = o_current_energy
        idx = 0
        for step in list_of_steps:
            trial = step * amplitude_tmp
            deformation = o_direction * trial
            try:
                deformed = ac_deformation(o_acontour, deformation, framesize, o_resolution)
                if deformed.shape[0] == 0:
                    break
            except Exception:
                break
            idx += 1
            energies[idx] = o_energy_function(deformed, o_context, True)
            
        if idx == 0:
            optimal_step_now = 0
        else:
            energies = energies[0:idx + 1]
            #print energies
            if npy.std(energies) == 0:
                optimal_step_now = 0
            else:
                energies = (energies - npy.mean(energies)) / npy.std(energies)
                #print energies
                list_of_steps = npy.insert(list_of_steps, 0, 0)
                list_of_steps = list_of_steps[:idx + 1]
                #print list_of_steps
                fit = npy.poly1d(npy.polyfit(list_of_steps, energies, min(6, idx)))
                optimal_step_now, fit_value, ierr, num = opt.fminbound(fit, 0, list_of_steps[-1], xtol = 0.1 * increment_limit, disp = 0, full_output = 1)
                #print optimal_step_now, fit_value
                min_ind = npy.argmin(energies)
                discrete_min = energies[min_ind]
                if fit_value > discrete_min:
                    optimal_step_now = list_of_steps[min_ind]
        #print optimal_step
        return optimal_step_now
                    
    # Reshaping
    optimal_amplitude = amplitude
    edge_vertices = npy.where((vertices[0, :] < 1) | (vertices[1, :] < 1) | (vertices[0, :] > framesize[0] - 2) | (vertices[1, :] > framesize[1] - 2) & (optimal_amplitude < 0))[0]
    if edge_vertices.shape[0] > 0:
        optimal_amplitude[edge_vertices] = -npy.min(npy.abs(optimal_amplitude))
        
    maximum = npy.max(npy.abs(optimal_amplitude))
    if maximum > 0:
        optimal_amplitude /= maximum
        
    if maximum > 0:
        if amplitude_limit >= 0:
            if amplitude_limit > 0:
                optimal_step = amplitude_limit
            else:
                optimal_step = maximum
        else:
            print optimal_amplitude
            optimal_step = n_optimal_step(optimal_amplitude)
            
        optimal_amplitude = optimal_step * optimal_amplitude
    else:
        optimal_step = 0
        
    return optimal_amplitude, optimal_step
    
def ac_deformation(acontour, deformation, framesize, resolution):
    vertices = acontour.copy()
    vertices[:, :-1] += deformation
    vertices[:, -1] = vertices[:, 0]
    
    deformed = vertices
    deformed = ac_resampling_spline(deformed, resolution)
    return deformed
    
def ac_mask(acontour, framesize):
    mask = npy.zeros(framesize, dtype = npy.uint8)
    new_acontour = npy.zeros([2, 5 * acontour.shape[1] - 4], dtype = npy.float32)
    
    s = acontour.shape[1]
    cnt = npy.arange(0, s) * 5
    spline = [0, 0]
    for i in range(2):
        spline[i] = itp.InterpolatedUnivariateSpline(cnt, acontour[i, :])
    for j in range(new_acontour.shape[1]):
        if j % 5 == 0:
            new_acontour[:, j] = acontour[:, j / 5]
        else:
            for i in range(2):
                new_acontour[i, j] = spline[i](j)
        
    fill_polygon([(int(x[1] + 0.5), int(x[0] + 0.5)) for x in new_acontour.transpose()], mask)
    return mask

def ac_resampling(acontour, resolution):
    resampled = acontour.copy()
    resolution **= 2
    
    vertices = acontour.copy()
    lengths = npy.sum(npy.diff(vertices, 1, 1) ** 2, 0)
    while vertices.shape[1] > 4 and npy.any(lengths < 0.36 * resolution):
        smallest = npy.argmin(lengths)
        if smallest == 0:
            smallest = 1
        vertices = npy.delete(vertices, smallest, 1)
        lengths[smallest - 1] = npy.sum((vertices[:, smallest] - vertices[:, smallest - 1]) ** 2)
        lengths = npy.delete(lengths, smallest)
    while npy.any(lengths > 2.56 * resolution):
        largest = npy.argmax(lengths)
        vertices = npy.insert(vertices, largest + 1, (vertices[:, largest] + vertices[:, largest + 1]) / 2, 1)
        lengths[largest] /= 4
        lengths = npy.insert(lengths, largest, lengths[largest])
    if npy.sign(po_orientation(vertices)) == npy.sign(po_orientation(acontour)):
        resampled = vertices
    return resampled
    
def ac_resampling_spline(acontour, resolution):
    import vtk
    points = vtk.vtkPoints()
    for i in range(acontour.shape[1] - 1):
        points.InsertPoint(i, acontour[0, i], acontour[1, i], 0)
        
    para_spline = vtk.vtkParametricSpline()
    para_spline.SetPoints(points)
    para_spline.ClosedOn()
    
    pt = [0.0, 0.0, 0.0]
    t = 0.05
    para_spline.Evaluate([t, t, t], pt, [0] * 9)
    l = npy.sqrt((pt[0] - acontour[0, 0]) ** 2 + (pt[1] - acontour[1, 0]) ** 2) / t
    cnt = int(l / resolution + 0.5)
    
    resampled = npy.zeros([2, cnt], dtype = npy.float32)
    resampled[:, 0] = acontour[:, 0]
    for i in range(1, cnt):
        t = i * 1.0 / cnt
        pt = [0.0, 0.0, 0.0]
        para_spline.Evaluate([t, t, t], pt, [0] * 9)
        resampled[:, i] = pt[:2]
    return resampled

if __name__ == "__main__":
    acontour = npy.array([[0, -10, 0, 10, 0],[10, 0, -10, 0, 10.0]])
    result = ac_resampling(acontour, 2)
    print result.shape
