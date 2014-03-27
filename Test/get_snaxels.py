'''
                            An Active Contour (Snake) Python Class

                                    Software version 1.0

                            (c) 2011 - 2013 Habib Jim Moukalled


FILE - get_snaxels.py

The following is the source for a Python Active Contour (Snake) Snaxel class. A snake is a
type of computerized spline used in many fields such as image processing, computer
vision, and medical image analysis for extracting image features. As a snake's energy
is minimized, the snake-spline will deform towards salient image features like gradient
magnitude, image intensity, and even line terminations. The vertices that describe a snake
have been termed "snaxe', in this file, we implement a function for creating a vector of snaxels.


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
from Snaxel import Snaxel;

def get_snaxels(contour):

    num_snaxels = numpy.shape(contour);
    num_snaxels = num_snaxels[0];
    vert = numpy.round(numpy.reshape(contour, (num_snaxels, 2)));

    # sort the list of vertices, before casting as snaxels.
    #vert.sort();
    
    snaxels = [];
    for i in range(0, num_snaxels):
        s = Snaxel(contour[i][0], contour[i][1]);
        snaxels.append(s);
    
    return snaxels, num_snaxels;
