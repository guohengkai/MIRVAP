'''
                            An Active Contour (Snake) Python Class

                                    Software version 1.0

                            (c) 2011 - 2013 Habib Jim Moukalled


FILE - Snake.py

The following is the source for a Python Active Contour (Snake) class. A snake is a
type of computerized spline used in many fields such as image processing, computer
vision, and medical image analysis for extracting image features. As a snake's energy
is minimized, the snake-spline will deform towards salient image features like gradient
magnitude, image intensity, and even line terminations.

In this Python Snake class, the Time-delayed Discrete Dynamic Programming algorithm
for minimizing snake-energy is implemented for snake-deformation. This algorithm was
first conceived by A. Amini, T. Weymouth, and R. Jain in:

        "Using Dynamic Programming for Solving Variational Problems in Vision",
        IEEE Transactions on Pattern Analysis and Machine Intelligence,
        September 1990 (vol. 12 no. 9).


                                    ** ATTENTION **
This software is distributed without any warrenties or technical support. However, if you
should find any bugs or issues, please report them to: habib.moukalled@gmail.com. Furthermore,
this software is intened to be used for educational and medicinal purposes. With this said,
you may download, use, modify, and redistribute this software and or its components given the
following:

    (1) This license is left in tact.

    (2) This software, and or components and algorithms are not sold.

    (3) By using this software, and or components and algorithms, you agree to the above terms.
'''

import numpy;
from get_min import get_min;
from Snaxel import Snaxel;


class Snake(object):
    # This information will exist in all Snakes.
    Name = 'Snake';
    description = 'A snake class implementing dynamic programming for energy minimization.';
    author = 'Habib Jim Moukalled';

    # Constructor.
    def __init__(self, snaxels, alpha, beta, delta_y, delta_x, images, weights):

        # The snaxels and total number of snaxels.
        self.snaxels = snaxels;
        self.num_snaxels = numpy.shape(snaxels);
        self.num_snaxels = self.num_snaxels[0];
        
        # The parameters governing the snake-spline's elasticity
        # (stretchiness) and rigidity (stiffness)respectively.
        self.alpha = alpha;
        self.beta = beta;

        # Maximum Energy
        self.BIG = 100000000000000000000000000000000000000000000000000000;
        self.Energy = self.BIG;

        # No iterations yet.
        self.num_iter = 0;
        
        # Relative coordinates of neighbors in the x-direction.
        scan_y = xrange(-delta_y, delta_y + 1);

        # The number of neighbors in the y-direction.
        num_neigh_y = numpy.shape(scan_y);
        num_neigh_y = num_neigh_y[0];
        
        # Relative coordinates of neighbors in the x-direction.
        scan_x = xrange(-delta_x, delta_x + 1);

        # The number of neighbors in the y-direction.
        num_neigh_x = numpy.shape(scan_x);
        num_neigh_x = num_neigh_x[0];

        # Total number of neighbors per snaxel.
        self.num_neigh = num_neigh_y * num_neigh_x;

        # Construct list of relative coordinates of neighbors.
        self.neighbors = [];
        for i in xrange(0, num_neigh_y):
            for j in xrange(0, num_neigh_x):
                s = Snaxel(scan_y[i], scan_x[j]);
                self.neighbors.append(s);

        # Construct Energy and Position tables use for dynamic programming.
        # This initializes every entry of Energy_Table to be BIG and every
        # entry of Position_Table to be a snaxel's original position.
        self.Energy_Table = self.BIG * numpy.ones((self.num_snaxels, self.num_neigh, self.num_neigh), numpy.float64);
        self.Position_Table = numpy.zeros((self.num_snaxels, self.num_neigh, self.num_neigh, 2), numpy.uint8);

        # Get the weights for the images that govern the snake's external forces.
        self.weights = weights;
        
        # The images associated with the current snake initialization.
        self.images = images;
        if numpy.size(self.weights) == 1:
            self.num_images = 1;
        else:
            self.num_images = numpy.shape(self.weights);
            self.num_images = self.num_images[0];


        # Get the image boundaries.
        size_vec = numpy.shape(self.images)
        y_boundary = size_vec[0];
        x_boundary = size_vec[1];
        self.y_boundary = y_boundary;
        self.x_boundary = x_boundary;

    # END of Constructor(snaxels, num_snaxels, alpha, beta, delta_x, delta_y, .


    # This function computes one iteration of time-delayed-discrete
    # dynamic programming for minimizing snake energy.
    def deform(self):
        self.ForwardPass();
        min_final_pos_next, min_final_pos_current, min_final_E = self.FindMinima();
        self.BackwardPass(min_final_pos_next, min_final_pos_current);
        self.Energy = min_final_E;
    # END of deform();

    # FORWARD PASS of DYNAMIC PROGRAMMING.
    def ForwardPass(self):
        
        for i in xrange(0, self.num_snaxels): # For all snaxels.
            
            min_pos_current = 0;
            min_pos_previous = 0;
                    
            for n in xrange(0, self.num_neigh): # neighbors of the next snaxel (v_i+1).

                # In general, the next snaxel is v_i+1, however, at the last snaxel,
                # the next snaxel does not exist, therefore, we define it to be
                # the first snaxel.
                if i == self.num_snaxels - 1:
                    n_snaxel = self.snaxels[0] + self.neighbors[n];
                else:
                    n_snaxel = self.snaxels[i + 1] + self.neighbors[n];
                
                if in_image_bounds(n_snaxel, self.y_boundary, self.x_boundary): # if the next snaxel's coordinates are within the image.                    
                    min_energy = self.BIG;

                    for c in xrange(0, self.num_neigh): # neighbors of current snaxel (v_i).

                        c_snaxel = self.snaxels[i] + self.neighbors[c];
                        #distance = numpy.sqrt((n_snaxel.y - c_snaxel.y)**2 + (n_snaxel.x - c_snaxel.x)**2);

                        if in_image_bounds(c_snaxel, self.y_boundary, self.x_boundary):# and distance <= 1: # other criteria may be added.

                            if i > 0: # if the previous snaxel (p_snaxel) is defined.
                                
                                min_energy = self.BIG;
                                
                                for p in xrange(0, self.num_neigh): # neighbors of previous snaxel (v_i-1).
                                    
                                    p_snaxel = self.snaxels[i - 1] + self.neighbors[p];

                                    if in_image_bounds(p_snaxel, self.y_boundary, self.x_boundary):
                                        
                                        energy = self.Energy_Table[i - 1, c, p] + self.E_int1(c_snaxel, p_snaxel) + self.E_int2(p_snaxel, c_snaxel, n_snaxel) + self.E_ext(c_snaxel);

                                        if i == self.num_snaxels - 1: # handle the last snaxel.
                                            energy = energy + self.E_ext(n_snaxel);

                                        if energy < min_energy:                                           
                                            min_energy = energy;
                                            min_pos_current = c;
                                            min_pos_previous = p;
                                            
                            else: # just handle the first snaxel.
                                
                                energy = self.E_int1(n_snaxel, c_snaxel);# + self.E_ext(c_snaxel);                               
                                if energy < min_energy:
                                    min_energy = energy;
                                    min_pos_current = c;
                                    min_pos_previous = 0;

                        # Update the Energy and Position tables to reflect
                        # the current minima.
                        self.Energy_Table[i, n, c] = min_energy;
                        self.Position_Table[i, n, c, 0] = min_pos_current;
                        self.Position_Table[i, n, c, 1] = min_pos_previous;
    # END of ForwardPass


    # Search the final column of the Energy Table to obtain minimum.
    def FindMinima(self):
        min_final_E = self.BIG;
        min_final_pos_next = 0;
        min_final_pos_current = 0;
        
        for n in xrange(0, self.num_neigh): # neighbors of next v_i+1.
            for c in xrange(0, self.num_neigh): # neighbors of current v_i.
                if self.Energy_Table[self.num_snaxels - 2, n, c] < min_final_E:
                    min_final_E = self.Energy_Table[self.num_snaxels - 2, n, c];
                    min_final_pos_next = n;
                    min_final_pos_current = c;
                    self.Energy = min_final_E;

        return min_final_pos_next, min_final_pos_current, min_final_E;



    # BACKWARDS PASS OF DYNAMIC PROGRAMMING.
    def BackwardPass(self, min_final_pos_next, min_final_pos_current):   
        pos_next = min_final_pos_next;
        pos_current = min_final_pos_current;

        for i in xrange(self.num_snaxels - 1, -1, -1):
            self.snaxels[i] = self.snaxels[i] + self.neighbors[pos_next];
            if i > 0:
                pos_next = self.Position_Table[i - 1, pos_next, pos_current, 0];
                pos_current = self.Position_Table[i - 1, pos_next, pos_current, 1];


                
    # Returns the first order internal snake-energy term:
    #       alpha |v_i - v_i-1|^2  , Eq. (49) in the paper.
    def E_int1(self, c_snaxel, p_snaxel):
        distance_squared = (c_snaxel.y - p_snaxel.y)**2 + (c_snaxel.x - p_snaxel.x)**2;
        return .5 * (self.alpha * distance_squared);



    # Returns the second order snake-energy term:
    #       beta*|v_i+1 -2v_i + v_i-1|^2  , Eq. (49) in the paper.
    def E_int2(self, p_snaxel, c_snaxel, n_snaxel):
        derivative = (n_snaxel.y - 2*c_snaxel.y + p_snaxel.y)**2 + (n_snaxel.x - 2*c_snaxel.x + p_snaxel.x)**2;
        return .5 * (self.beta * derivative);



    def E_ext(self, snaxel):
        ExternalEnergy = 0;
        if self.num_images == 1:
            ExternalEnergy = (self.weights * self.images[snaxel.y, snaxel.x]);
        else:
            for i in xrange(0, self.num_images):
                ExternalEnergy = ExternalEnergy + (self.weights[i] * self.images[snaxel.y, snaxel.x, i]);
        #return self.w_line*self.image[snaxel.x, snaxel.y] -self.w_edge*self.grad_mag[snaxel.x, snaxel.y];
        #print 'ExternalEnergy(%d, %d) = %d.' %(snaxel.x, snaxel.y, ExternalEnergy);
        return ExternalEnergy;



    # This function will minimize snake-energy, until the snake achieves equilibrium.
    def MinimizeEnergy(self):
        E_old = -1;
        E_new = self.BIG;
        while (E_old != E_new) and self.num_iter < 42:
            E_old = E_new;
            self.deform();
            E_new = self.Energy;
            self.num_iter = self.num_iter + 1;
            print 'Iteration # %d, Snake-Energy = %d.' % (self.num_iter, self.Energy);
                
                
    # A method to display the current configuration of the snake.
    def print_configuration(self):
        #print self.Name;
        print ' ';
        print '###############################################';
        print '# A snake with the following configuration';
        print '# has been created for a given image:';
        print '###############################################';
        print '# ' ;

        print '# alpha = %f.' % self.alpha;
        print '# beta = %f.' % self.beta;
        print '# Number of neighbors = %d' % self.num_neigh;


    # This method will print out the list of snaxels that comprise our snake.
    def print_snaxels(self):
        print ' ';
        print '%d SNAXELS = [' % self.num_snaxels;
        for i in range(0, self.num_snaxels):
            self.snaxels[i].print_snaxel();
        print '\t\t].';


    # This method will print out the relative coordinates of neighboring snaxels.
    def print_neighbors(self):
        print ' ';
        print '%d NEIGHBORS = [' % self.num_neigh;
        for i in xrange(0, self.num_neigh):
            self.neighbors[i].print_snaxel();
        print '\t\t].';

        
# A BOOLEAN function to check if snaxels are
# within the image boundaries.
def in_image_bounds(snaxel, y_boundary, x_boundary):
    if snaxel.y > -1 and snaxel.y < y_boundary and snaxel.x > -1 and snaxel.x < x_boundary:
        return True;
    else:
        return False;
