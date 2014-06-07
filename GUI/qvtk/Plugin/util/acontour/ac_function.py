# -*- coding: utf-8 -*-
"""
Created on 2014-06-06

@author: Hengkai Guo
"""

import numpy as npy
import scipy.interpolate as itp
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

def ac_flattening(acontour):
    return acontour[:, :-1]
def ac_normal(acontour):
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
        direction[0, j] = -tangent[1]
        direction[1, j] = tangent[0]
        direction[:, j] /= npy.sqrt(npy.sum(direction[:, j] ** 2))
    return direction
def ac_amplitude(vertices, amplitude, amplitude_limit, framesize, o_acontour, \
        o_direction, o_previous_steps, o_current_energy, o_energy_function, o_resolution, o_context):
    # Reshaping
    optimal_amplitude = amplitude
    edge_vertices = npy.where((vertices[0, :] < 1) | (vertices[1, :] < 1) | (vertices[0, :] > framesize[0] - 2) | (vertices[1, :] > framesize[1] - 2) & (optimal_amplitude < 0))[0]
    if edge_vertices.shape[0] > 0:
        optimal_amplitude[edge_vertices] = -npy.min(npy.abs(optimal_amplitude))
        
    maximum = npy.max(npy.abs(optimal_amplitude))
    if maximum > 0:
        optimal_amplitude /= maximum
        optimal_step = amplitude_limit
        optimal_amplitude = optimal_step * optimal_amplitude
    else:
        optimal_step = 0
        
    return optimal_amplitude, optimal_step
    
def ac_deformation(acontour, deformation, framesize, resolution):
    vertices = acontour.copy()
    vertices[:, :-1] += deformation
    vertices[:, -1] = vertices[:, 0]
    
    deformed = vertices
    deformed = ac_resampling(deformed, resolution)
    return deformed
    
def ac_mask(acontour, framesize):
    mask = npy.zeros(framesize, dtype = npy.uint8)
    fill_polygon([(int(x[1] + 0.5), int(x[0] + 0.5)) for x in acontour.transpose()], mask)
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

if __name__ == "__main__":
    acontour = npy.array([[0, -10, 0, 10, 0],[10, 0, -10, 0, 10.0]])
    result = ac_resampling(acontour, 2)
    print result.shape
