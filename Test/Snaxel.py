'''
                            An Active Contour (Snake) Python Class

                                    Software version 1.0

                            (c) 2011 - 2013 Habib Jim Moukalled


FILE - Snaxel.py

The following is the source for a Python Active Contour (Snake) Snaxel class. A snake is a
type of computerized spline used in many fields such as image processing, computer
vision, and medical image analysis for extracting image features. As a snake's energy
is minimized, the snake-spline will deform towards salient image features like gradient
magnitude, image intensity, and even line terminations. The vertices that describe a snake
have been termed 'snaxel', in this basic class, we implement the snaxel (vertex).


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

import operator;

class Snaxel(object):
    Name = 'snaxel';
    description = 'A single vertex along the active contour.';
    author = 'Habib Jim Moukalled';

    def __init__(self, y, x):
        self.y = int(y);
        self.x = int(x);
        
    def __add__(self, other):
        return Snaxel(self.y + other.y, self.x + other.x);
    
    def __sub__(self, other):
        return Snaxel(self.y - other.y, self.x - other.x);
    
    def __mul__(self, other):
        return Snaxel(self.y * other.y, self.x * other.x);

    #def __mul_(self, int):
    #    return Snaxel(int * self.x, int * self.y);
    
    def __eq__(self, other):
        return (self.y == other.y) and (self.x == other.x);

    def __ne__(self, other):
        if (self.y != other.y) or (self.x != other.x):
            return True;
        else:
            return False;
        
    def print_snaxel(self):
        print '\t (%d, %d)' %(self.y, self.x);
