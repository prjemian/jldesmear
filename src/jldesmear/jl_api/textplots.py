#!/usr/bin/env python

'''
Make charts on a text console using character graphics

Generate graphical output on a text console.
These routines predate modern GUI environments.
While the output may look rough, they work just about anywhere.

Here is how the code may be called::

    >>> fn = toolbox.GetTest1DataFilename('.smr')
    >>> x, y, dy = toolbox.GetDat(fn)
    >>> print("Data plot: " + fn)
    >>> Screen().xyplot(x, y)

Example, given *C(q)* and *S(q)*::

    KratkyPlot = textplots.Screen()
    title = "\\nKratky plot, I * q^2 vs q: S=smeared"
    q2C = q*q*(C - B)
    q2S = q*q*(S - B)
    KratkyPlot.SetTitle(title)
    KratkyPlot.addtrace(lnq, q2S, "S")
    KratkyPlot.printplot()
    title = "\\nKratky plot, I * q^2 vs q: C=input, S=smeared"
    KratkyPlot.SetTitle(title)
    KratkyPlot.addtrace(lnq, q2C, "C")
    KratkyPlot.printplot()

with the right data, produces plots of :math:`q^2 C(q)` and :math:`q^2 S(q)`::

    Kratky plot, I * q^2 vs q: C=input, S=smeared
    x: min=-7.898   step=0.0889226   max=-1.49558
    y: min=-0.107876   step=0.199276   max=4.2762
     ------------------------------------------------------------------------- 
    |           C                                                             |
    |        CCCCCC                                                           |
    |      CCC    CCC                                                         |
    |     CC        CC                                                        |
    |    CC          CC                                                       |
    |   CC            C                                                       |
    |   C              C                                                      |
    |  C                C                                                     |
    | CC                CC                                                    |
    |CC                  C                                                    |
    |                     C                                                   |
    |C                    CC                                                  |
    |                      C                                                  |
    |                       C                                                 |
    |                        C                                                |
    |                         C                                               |
    |                         CC                                              |
    |                           C                                             |
    |                            CC                                           |
    |                             CC                                          |
    |                               CCC                                       |
    |                                  CCCCCC                            CCCC |
    |SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC|
     ------------------------------------------------------------------------- 

Source code documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''


import copy
import toolbox
import os       #@UnusedImport
import numpy


class Screen:
    '''plotting canvas'''

    def __init__(self, MaxRow = 25, MaxCol = 75, Symbol = 'O'):
        '''declare initial storage'''
        self.MaxRow = MaxRow
        self.MaxCol = MaxCol
        self.Symbol = Symbol
        self.blank = ' '
        self.hBordr = '-'
        self.vBordr = '|'
        self.buffer = []
        self.title = ''
        self.traces = []
        self.comments = ''

    def make_buffer(self, rows = None, cols = None):
        '''prepare a screen buffer'''
        if rows == None:
            rows = self.MaxRow
        if cols == None:
            cols = self.MaxCol
        row = [self.blank]*cols
        screen = []
        for i in range(rows):
            screen.append(copy.deepcopy(row))
        # paint the plot border on the screen
        for i in range(cols-2):
            screen[0][i+1] = self.hBordr
            screen[-1][i+1] = self.hBordr
        for i in range(rows-2):
            screen[i+1][0] = self.vBordr
            screen[i+1][-1] = self.vBordr
        return screen

    def addtrace(self, x, y, symbol = "O"):
        ''' 
        add the (x,y) trace to the plot with the given symbol

        :param x: array (list) of abcissae
        :param y: array (list) of ordinates
        :param symbol: plotting character 
        '''
        trace = {}
        trace['xMin'], trace['xMax'] = self.__minmaxlist(x)
        trace['yMin'], trace['yMax'] = self.__minmaxlist(y)
        trace['symbol'] = symbol
        trace['x'] = copy.deepcopy(x)
        trace['y'] = copy.deepcopy(y)
        self.traces.append(trace)

    def paintbuffer(self):
        ''' 
        plot the traces on the screen buffer
        data scaling functions are offset by +1 for plot frame
        '''
        if len(self.traces) < 1:
            return      # nothing to show
        xMin, xMax, yMin, yMax = None, None, None, None
        for trace in self.traces:
            xMin, xMax = self.__minmax(xMin, xMax, trace['xMin'])
            xMin, xMax = self.__minmax(xMin, xMax, trace['xMax'])
            yMin, yMax = self.__minmax(yMin, yMax, trace['yMin'])
            yMin, yMax = self.__minmax(yMin, yMax, trace['yMax'])
        # loop through the traces and find min and max for x and y,
        # set scale factors, then add traces to the buffer
        # then show the buffer
        ColDel = (self.MaxCol - 3) / (xMax - xMin)
        RowDel = (self.MaxRow - 3) / (yMax - yMin)
        self.buffer = self.make_buffer()    # clear the buffer
        for trace in self.traces:
            for i in range(len(trace['x'])):
                c = int(ColDel * (trace['x'][i] - xMin)) + 1
                r = int(RowDel * (trace['y'][i] - yMin)) + 1
                self.buffer[r][c] = trace['symbol']
        self.comments = ''
        if len(self.title.strip())>0:
            self.comments += self.title + "\n"
        fmt = "%s: min=%g   step=%g   max=%g\n"
        self.comments += fmt % ("x", xMin, 1/ColDel, xMax)
        self.comments += fmt % ("y", yMin, 1/RowDel, yMax)

    def printplot(self):
        ''' plot to stdout '''
        print(str(self))

    def __str__(self):
        ''' :return: plot as a string '''
        self.paintbuffer()
        txt = ""
        if len(self.traces) > 0:
            txt += self.comments
            txt += repr(self)
        return txt

    def __repr__(self):
        '''default representation of this structure is ASCII'''
        txt = ""
        for row in self.buffer:
            line = "".join(row)
            txt = line + "\n" + txt  # bottom to top
        return txt

    def __minmaxlist(self, x):
        '''
        return the minimum and maximum of the array

        :param numpy.ndarray x: array to be examined
        '''
        return x.min(), x.max()

    def __minmax(self, lo, hi, value):
        '''
        return the minimum and maximum of the value

        :param float lo: current minimum or None if not set
        :param float hi: current maximum or None if not set
        :param float value: value to be tested
        :return: lo = min(lo,value), hi = max(hi, value)
        :rtype: (float, float)
        '''
        if lo == None: lo = value
        if hi == None: hi = value
        if value < lo: lo = value
        if value > hi: hi = value
        return lo, hi

    def SetTitle(self, title):
        '''
        define a plot title

        :param str title: the title of the plot
        '''
        self.title = title

    def xyplot(self, x, y, title = None):
        '''
        convenience to plot *y(x)*

        :param numpy.ndarray x: abcissae
        :param numpy.ndarray y: ordinates
        '''
        if title == None:
            self.SetTitle("plot of y vs x, %d points" % len(x))
        else:
            self.SetTitle(title)
        self.addtrace(x, y)
        self.printplot()

    def residualsplot(self, z, title = None):
        '''
        convenience to plot *z* vs point number

        :param numpy.ndarray z: ordinates (standardized residuals)
        '''
        n = numpy.linspace(1, len(z), len(z))
        # generate pseudo-data for the +1, -1, and 0 bars
        npm = numpy.linspace(1, self.MaxCol, self.MaxCol) * len(z)/self.MaxCol
        zeros = numpy.zeros_like(npm)
        plus = numpy.ones_like(npm)
        minus = -1 * plus
        if title == None:
            self.SetTitle("plot of standardized residuals vs index")
        else:
            self.SetTitle(title)

        self.addtrace(npm, plus, "=")
        self.addtrace(npm, minus, "=")
        self.addtrace(npm, zeros, "~")
        self.addtrace(n, z, "+")
        self.printplot()


def __demo():
    '''show the various routines'''
    print("Testing $Id$")
    fn = toolbox.GetTest1DataFilename('.smr')
    x, y, _ = toolbox.GetDat( fn )
    print("\nData plot: " + fn)
    _ = Screen().xyplot(x, y)

    title = "\nResiduals plot: " + fn
    # create test some data that looks sort of like residuals
    avg = y.sum() / len(y)
    z = y / avg
    scr = Screen()
    scr.residualsplot(z, title)


if __name__ == "__main__":
    __demo()
