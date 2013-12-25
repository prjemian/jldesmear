#!/usr/bin/env python

'''
General mathematical toolbox routines

The routines that follow are part of my general
mathematical "toolbox".  Some of them are taken
(with reference) from book(s) but most, I have
developed on my own.  They are modular in construction
so that they may be improved, as needed.
'''


import os
import sys
import math
import string
import numpy


def AskQuestion(question, answer):
    '''
    request a string, float, or int from the command line

    :param str question: string to pose
    :param answer: default answer
    :type answer: string | float | int
    :return: final answer
    :rtype: str | float | int
    '''
    print "%s <%s> ==> " % (question, answer), 
    reply = raw_input()
    if len(reply) == 0:
        reply = answer
    return reply


def AskString(question, answer):
    '''
    request a string from the command line

    :param str question: string to pose
    :param str answer: default answer
    :return: final answer
    :rtype: str
    '''
    return AskQuestion(question, answer).strip()


def AskDouble(question, answer):
    '''
    request a double from the command line

    :param str question: string to pose
    :param double answer: default answer
    :return: final answer
    :rtype: double
    '''
    return float(AskQuestion(question, answer))


def AskInt(question, answer):
    '''
    request an integer from the command line

    :param str question: string to pose
    :param int answer: default answer
    :return: final answer
    :rtype: int
    '''
    return int(AskQuestion(question, answer))


def AskYesOrNo(question, answer):
    '''
    one of two choices seems simple

    :param str question: string to pose
    :param str answer: default answer
    :return: ``y | n``
    :rtype: str
    '''
    choices = ("y", "n")
    new_question = "%s (Y=yes, N=no)" % question
    reply = ""
    while not reply in choices:
        reply = AskQuestion (new_question, answer)
        if len(reply.strip()) > 0:
            reply = string.lower(reply.strip()[0])
    return reply


def Spinner(i, quiet = False):
    '''
    Spins a stick to indicate program is still working.
    Call this routine frequently during long operations to show progress.

    :param int i: selector (increment this in the calling routine)
    :param bool quiet: optional switch to turn off the spinner
    '''
    if not quiet:
        sym = ("-", "/", "|", "\\")
        sys.stdout.writelines("%c%c" % (sym[i % 4], 0x08))
        sys.stdout.flush()


def isDataLine (line):
    '''
    test if a given line of text is not blank or commented out

    :param string line: line of text from an input file (usually)
    :return: True | False
    :rtype: bool
    '''
    isData = False
    s = line.strip()
    if len(s):        # only consider non-blank lines */
        if s[0] != '#': # but don't count comment lines */
            isData = True
    return isData


def GetDat (infile):
    '''
    read three-column data from a wss (white-space-separated) file
    
    Data appear as Q  I  dI with one data point per line.
    A "#" may be used to comment out any line.
    
    :param string infile: name of input data file
    :return: x, y, dy
    :rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray)
    '''
    try:
        x, y, dy = numpy.loadtxt(infile, 
                      dtype=numpy.float, 
                      comments='#',
                      unpack=True)
        return x, y, dy
    except:
        message = "GetDat: error while opening or reading: " + infile
        raise RuntimeError, message


def SavDat (outfile, x, y, dy):
    '''
    save three column ASCII data in tab-separated file

    :param str outfile: name of output file 
    :param numpy.ndarray x: column 1 data array
    :param numpy.ndarray y: column 2 data array 
    :param numpy.ndarray dy: column 3 data array
    '''
    try:
        numpy.savetxt(outfile, 
                      numpy.transpose([x, y, dy]),
                      fmt='%g',
                      delimiter='\t')
        print("Saved data in file: %s\n" % outfile)
        return outfile
    except:
        print "SavDat: error while opening or writing: " + outfile
        raise


def Iswap (a, b):
    ''':return: (tuple) of (b, a)'''
    return b, a

iLo = iHi = 0       # for use by Bsearch

def BSearch(z, x):
    '''
    Binary search the array **x** for ``x[iLo] <= z < x[iHi]``
    On exit, ``iLo`` and ``iHi`` will exactly bracket the datum
    and ``iTest`` will be the same as ``iLo``.
    If ``z`` is below [above] the range, ``iTest = -1 [NumPts+1]``.

    :param float z: value to find
    :param numpy.ndarray x: array to be searched
    :return: (True|False, iTest)  
    :rtype: (bool, int)
    '''
    # TODO: can numpy do this faster?
    global iLo, iHi
    iTest = -1                 # assume that z < x[1] and test
    if (z < x[0]): return (False, iTest)
    NumPts = len(x)
    iTest = NumPts             # assume z > x[n] and test
    if (z > x[-1]): return (False, iTest)
#     return (True, x.searchsorted(z))
    if (iLo < 0 or iHi >= NumPts or iLo >= iHi):
        iLo = 0
        iHi = NumPts - 1
    while (z < x[iLo]):
        iLo /= 2
    while (z > x[iHi]):         # expand up?
        iHi = (iHi + 1 + NumPts) / 2
    iTest = iHi
    while (iHi - iLo > 1):
        iTest = (iLo + iHi) / 2
        if (z >= x[iTest]):
            iLo = iTest
        else:
            iHi = iTest
    iTest = (iLo + iHi) / 2
    return (True, iTest)


def strtrim (txt):
    ''' 
    cut out any white space from the string 
    (compatibility method for legacy code only)
    '''
    return txt.strip()


def linear_interpolation(x,x1,y1,x2,y2):
    '''
    linear interpolation

    :param float x: lookup value
    :param float x1: x at point 1
    :param float y1: y at point 1
    :param float x2: x at point 2
    :param float y2: y at point 2
    :return: y(x): linear interpolation from (x1,y1) and (x2,y2)
    :rtype: float
    '''
    return  (y1 + (y2-y1) * (x-x1) / (x2-x1))


def log_interpolation(x,x1,y1,x2,y2):
    '''
    logarithmic (log vs linear) interpolation

    :param float x: lookup value
    :param float x1: x at point 1
    :param float y1: y at point 1
    :param float x2: x at point 2
    :param float y2: y at point 2
    :return: y(x): logarithmic interpolation from (x1,y1) and (x2,y2)
    :rtype: float
    '''
    b = linear_interpolation(x,x1,math.log(y1),x2,math.log(y2))
    return  math.exp(b)


def find_first_index(x, target):
    '''
    find i such that x[i] >= target and x[i-1] < target

    :param ndarray x: array to search
    :param float target: value to bracket
    :return: index of array x or None
    :rtype: int
    '''
    i = x.searchsorted(target)
    if i < len(x):
        return i
    return None


def GetTest1DataFilename(ext='.smr'):
    '''find the test1 data in the package'''
    path = os.path.dirname(__file__)
    filename = os.path.join(path, '..', 'data', 'test1'+ext)
    return os.path.abspath(filename)


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
