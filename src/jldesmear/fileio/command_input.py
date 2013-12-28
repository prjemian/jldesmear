#!/usr/bin/env python

'''support traditional command-line input format'''


import os
from fileio import FileIO
from jldesmear.api.info import Info
from jldesmear.api.extrapolation import discover_extrapolations


class CommandInput(FileIO):
    '''
    command input file format
    
    This file format was created to pipe the inputs
    directly to the interactive command-line
    FORTRAN program.  There were two benefits:
    
    #. desmearing parameters were documented in a file
    #. the answer to each question was automatically provided
    
    contents::
    
        SMR_filename        (absolute path or relative to directory of .inp file)
        DSM_filename
        slitlength
        extrapolation_method
        sFinal
        number_iterations
        feedback_method
        
    .. index:: QRS
    
    The file names (SMR and DSM) are given as either 
    absolute or relative to the directory of the 
    *.inp* file.  The data are stored in three-column ASCII,
    with whitespace separators with the columns *Q I dI*.  
    Individual data points may be commented out by placing
    a ``#`` character at the start of that line of text.
    This format is known to some as *QRS*.

    The *slitlength* and *sFinal* are given as floating point
    numbers in the same units as :math:`q`.  It is expected
    that ``sFinal < qMax`` by at least a few data points.
    
    Example ``test1.inp`` file::
    
        test1.smr
        test1.dsm
        0.08
        linear
        0.08
        20
        fast

    '''

    description = 'command input'
    extensions = ['*.inp', ]
    
    def read(self, filename):
        '''
        read desmearing parameters from a command input file
        
        :param str filename: full path to the command input file
        :returns: instance of :class:`jldesmear.api.info.Info`
        '''
        def get_buf_item(key, item=0):
            return buf[key].split()[item]

        ext = '.inp'
        if not filename.endswith(ext): return None
        if not os.path.exists(filename): return None

        self.info = Info()

        # read a .inp file
        self.info.parameterfile = filename
        path = os.path.dirname(filename)
        owd = os.getcwd()
        os.chdir(path)
        buf = open(os.path.abspath(filename), 'r').readlines()
        if len(buf) < 7:
            msg = "not enough information in command input file: " + filename
            raise RuntimeError, msg
        
        functions = discover_extrapolations()
        
        self.info.infile = os.path.abspath(os.path.join(path, get_buf_item(0)))
        self.info.outfile = os.path.abspath(os.path.join(path, get_buf_item(1)))
        self.info.slitlength = float(get_buf_item(2))
        self.info.extrapname = get_buf_item(3)
        self.info.sFinal = float(get_buf_item(4))
        self.info.NumItr = int(get_buf_item(5))
        self.info.LakeWeighting = get_buf_item(6)
        self.info.extrap = functions[self.info.extrapname]
        self.info.quiet = True
        self.info.callback = None

        os.chdir(owd)
        
        return self.info
    
    def save(self, filename):
        '''
        write desmearing parameters to a command input file
        '''
        path = os.path.abspath(os.path.dirname(filename))
        owd = os.getcwd()
        os.chdir(path)

        f = open(filename, 'w')
        if path == os.path.dirname(self.info.infile):
            fn = os.path.split(self.info.infile)[1]
        else:
            fn = self.info.infile
        f.write(fn + '\n')
        if path == os.path.dirname(self.info.outfile):
            fn = os.path.split(self.info.outfile)[1]
        else:
            fn = self.info.outfile
        f.write(fn + '\n')
        f.write(str(self.info.slitlength) + '\n')
        f.write(self.info.extrapname + '\n')
        f.write(str(self.info.sFinal) + '\n')
        f.write(str(self.info.NumItr) + '\n')
        f.write(self.info.LakeWeighting + '\n')
        f.close()

        os.chdir(owd)


class AnyFile(FileIO):

    description = 'any file'
    extensions = ['*.*', ]
    
    # TODO: this should not read any files
    # Rather, files read by this class should be checked
    # to see if they can be read by another support.


def main():
    from jldesmear.api import toolbox
    ext = '.inp'
    fn = toolbox.GetTest1DataFilename(ext)
    info = CommandInput()
    parms = info.read(fn)
    print str(parms)
    info.save('junk.inp')


if __name__ == "__main__":
    main()
