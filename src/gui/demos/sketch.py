#!/usr/bin/env python

'''
simple Traits demo
'''


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


from traits.api import *
from traitsui.api import *
import math

class Left(HasTraits):
    """ demo object """

    lhs1 = String
    lhs2 = Enum('one', 'apple', 'island', 14, math.pi, __file__)
    
    def _lhs2_changed(self):
        self.lhs1 = str(self.lhs2)

class Right(HasTraits):
    ''' another object '''
    pilgrim = Float
    joe = Range(-5.0, 5, 0)
    
    def _joe_changed(self):
        self.pilgrim = self.joe

class Container(HasTraits):
    ''' arranges and shows the widgets '''
    left = Instance(Left, ())
    right = Instance(Right, ())

    view = View(
                HSplit(
                        Item('left', style='custom', show_label=False, ),
                        Item('right', style='custom', show_label=False, ),
                       ),
               )

bucket = Container()
bucket.left.lhs2 = 'apple'
bucket.right.joe = math.exp(1)
bucket.configure_traits()

