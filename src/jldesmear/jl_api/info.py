#!/usr/bin/env python

''' 
desmearing parameters::

    infile = ""                     # input data file
    outfile = ""                    # output data file
    slitlength = 1.0                # slit length (l_o) as defined by Lake
    sFinal = 1.0                    # fit extrapolation constants for q>=sFinal
    NumItr = INFINITE_ITERATIONS    # number of desmearing iterations
    extrapname = "constant"         # model final data as a constant
    LakeWeighting = "fast"          # shows the fastest convergence most times
    extrap = None                   # extrapolation function object
    quiet = False                   # suppress output from desmearing operations
    callback = None                 # function object to call after each desmearing iteration
'''


INFINITE_ITERATIONS = 'INFINITE_ITERATIONS'


class Info(object):
    ''' parameters used by the desmearing methods '''
    
    filename = ""                   # file containing these terms
    infile = ""                     # input data
    outfile = ""                    # output data
    slitlength = 1.0                # slit length (l_o) as defined by Lake
    sFinal = 1.0                    # fit extrapolation constants for q>=sFinal
    NumItr = INFINITE_ITERATIONS    # number of desmearing iterations
    extrapname = "constant"         # model final data as a constant
    LakeWeighting = "fast"          # shows the fastest convergence most times
    extrap = None                   # extrapolation function object
    quiet = True                    # suppress progress indicator (spinner) output during smearing
    callback = None                 # function object to call after each desmearing iteration
    
    parameterfile = ''              # name of file with program parameters
    fileio_class = None             # file format support class

    def __str__(self):
        ''' canonical string representation '''
        s = []
        #s.append( repr(self) )
        if len(self.parameterfile):
            s.append( 'parameterfile: %s' % self.filename )
        s.append( 'infile: %s' % self.infile )
        s.append( 'outfile: %s' % self.outfile )
        s.append( 'slitlength: %g' % self.slitlength )
        s.append( 'sFinal: %g' % self.sFinal )
        s.append( 'NumItr: %s' % str(self.NumItr) )
        s.append( 'extrapname: %s' % self.extrapname )
        s.append( 'LakeWeighting: %s' % self.LakeWeighting )
        s.append( 'extrap: %s' % str(self.extrap) )
        s.append( 'quiet: %s' % self.quiet )
        #s.append( 'callback: %s' % str(self.callback) )
        return "\n".join(s)

    def moreIterationsOk(self, iteration_count):
        '''
        :return: is it OK to take more iterations?
        :rtype: bool
        '''
        infinite = self.NumItr == INFINITE_ITERATIONS
        return infinite or iteration_count < abs(self.NumItr)
