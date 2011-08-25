#!/usr/bin/env python

'''
Lake desmearing GUI using Enthought's Chaco and Traits packages.
'''


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


import os, sys
# make sure lake is on the path, as well
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))

import lake.toolbox
import lake.desmear
import lake.info

#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'


#from enthought.chaco.shell import plot, show
from traits.api \
    import *

from traitsui.api \
    import *

from enthought.chaco.chaco_plot_editor \
    import ChacoPlotItem


class Gui(HasTraits):
    ''' Provide interactive access to all the parameters used in desmearing
    
    This is a main GUI.  It uses Traits.  Call it with code like this::

        gui = Gui()
        gui.configure_traits(filename=paramfile)

    '''
    infile = File(label="in", desc="the name of the input smeared SAS data file", )
    outfile = File(label="out", desc="the name of the output desmeared SAS data file", )
    l_o = Float(label="slit length", desc="slit length, as defined by Lake", )
    qFinal = Float(label="qFinal", desc="fit extrapolation constants for Q>=qFinal",)
    NumItr = Int(label="# iterations", desc="number of desmearing iterations",)
    extrapolation = Enum( 
                 'constant',  'linear', 'powerlaw', 'Porod',
                 label="Extrapolation", desc="form of extrapolation",)
    LakeWeighting = Enum( 
                 'constant', 'fast',  'ChiSqr',
                 label="weighting", desc="weighting method for iterative refinement",)

    btnDesmear = Button("desmear")
    btnClearConsole = Button("clear console")

    console_text = String

    status_label = String('status:')
    status_msg = String

    Qvec = []
    smr = []
    smr_esd = []
    dsmI = []
    dsmI_esd = []
    z = []

    def _infile_default(self): return os.path.join('..', '..', 'data', 'test1.smr')
    def _l_o_default(self): return 0.08
    def _qFinal_default(self): return 0.08
    def _NumItr_default(self): return 10
    def _extrapolation_default(self): return 'linear'
    def _LakeWeighting_default(self): return 'fast'

    def _infile_changed(self):
        if len(self.infile) == 0:
            return
        if os.path.exists(self.infile):
            try:
                self.Qvec, self.smr, self.smr_esd = lake.toolbox.GetDat(self.infile)
                self.z = [0 for x in self.Qvec]
                self.post_message("read %d points from %s" % (len(self.Qvec), self.infile) )
            except:
                self.post_message("could not read data from %s" % self.infile)
                self.infile = ""
        else:
            self.post_message("%s does not exist" % self.infile)
            self.infile = ""
        
    def _btnClearConsole_fired(self):
        ''' clear the console widget '''
        self.console_text = ""
        self.status_msg = "console cleared"

    def _console_text_changed(self):
        # TODO: scroll to last line in view and force UI update/redraw
        #try:
        #    print self.trait( 'traits_view' ).inner_traits
        #    print self.trait( 'traits_view' ).trait_type
        #    print self.trait( 'traits_view' ).parent
        #    print self.trait( 'traits_view' ).type
        #except:
        #    print sys.exc_info()
        #sys.stdout.flush()
        pass

    def _status_msg_changed(self):
        if len(self.console_text):
            self.console_text += "\n"
        self.console_text += self.status_msg
            
    def _btnDesmear_fired(self):
        ''' start desmearing '''
        self.post_message("desmear button clicked")
        if len(self.Qvec) == 0:
            self.post_message("cannot desmear now, no data")
            return
        if len(self.Qvec) != len(self.smr):
            self.post_message("cannot desmear now, number of data points inconsistent")
            return
        if len(self.Qvec) != len(self.smr_esd):
            self.post_message("cannot desmear now, number of data points inconsistent")
            return
        if self.qFinal > self.Qvec[-2]:
            self.post_message("cannot desmear now, fit range beyond data range")
            return

 	params = lake.info.Info()
 	if params == None:
            self.post_message("serious: could not get an Info() object")
 	    return	    # no input file so bail out

        params.infile = self.infile
        params.outfile =  self.outfile
        params.slitlength =  self.l_o
        params.sFinal =  self.qFinal
        params.NumItr =  self.NumItr
        params.extrapname = self.extrapolation
        params.LakeWeighting = self.LakeWeighting
	params.callback = self.my_callback

        dsm = lake.desmear.Desmearing( self.Qvec, self.smr, self.smr_esd, params )
	dsm.traditional()
        # TODO: need to plot final result
        # TODO: offer to save final result
    
    def my_callback (self, dsm):
        '''
        this function is called after every desmearing iteration
        from :func:`lake.desmear.Desmearing.traditional()`
    
        :param obj dsm: desmearing parameters object
        :return: should desmearing stop?
        :rtype: bool
        '''
	fmt = "#%d  ChiSqr=%g  %s"
	msg = fmt % (dsm.iteration_count, dsm.ChiSqr[-1], str(dsm.params.extrap) )
        self.post_message( msg )
        # TODO: How to update the residuals chart?
        self.z = list( dsm.z )
        #self._residuals_plot.window.control.Update()
	more_steps_ok = dsm.params.moreIterationsOk(dsm.iteration_count)
        return not more_steps_ok
    
    def post_message(self, msg):
        self.status_msg = msg
    
    # TODO: need loglog plot
    _sas_plot = ChacoPlotItem(
        "Qvec", "smr", 
        resizable=True,
        y_label="scattering",
        x_label="Q",
        label="I(Q)", 
        title="", 
        springy=True,
        show_label=False,
    )
    # TODO: need linlog plot -- perhaps change from a ChacoPlotItem to a plot inside an item
    _residuals_plot = ChacoPlotItem(
        "Qvec", "z", 
        resizable=True,
        y_label="residuals",
        x_label="Q",
        label="z(Q)", 
        title="", 
        springy=True,
        show_label=False,
    )
    # see: http://github.enthought.com/traitsui/traitsui_user_manual/handler.html#controlling-the-interface-the-handler
    traits_view = View(
        HSplit(
            Group(
                Group(
                         Item('infile', show_label=False),
                         label="input data file name",
                         show_border = True,
                      ),
                Group(
                         Item('l_o'),
                         Item('qFinal'),
                         Item('NumItr'),
                         Item('extrapolation'),
                         Item('LakeWeighting'),
                         label="adjustable parameters",
                         show_border = True,
                      ),
                HGroup(
                        Item('btnDesmear', show_label=False),
                        spring,
                        Item('btnClearConsole', show_label=False),
                        label="buttons",
                        show_border = True,
                     ),
                Group(
                         Item('outfile', show_label=False),
                         label="output data file name",
                         show_border = True,
                      ),
                Group(
                        Item("console_text", 
                             springy=True, 
                             style='custom', 
                             show_label=False, 
                        ),
                        label="console output",
                        show_border = True,
                  ),
            ),
            VSplit(
                _sas_plot,
                _residuals_plot,
            ),
        ),
        resizable = True,
        title="Lake/Jemian Desmearing GUI",
        width=700,
        height=500,
        statusbar = [
            StatusItem(name = 'status_label', width = 80),
            StatusItem(name = 'status_msg', width = 0.5),
        ],
        buttons=NoButtons,
    )
    
def main(paramfile = None):
    if paramfile == None:
        path = os.path.abspath( os.path.dirname(__file__) )
        name = os.path.basename( os.path.splitext(__file__)[0] )
        paramfile = os.path.join(path, name + '.pkl')
    gui = Gui()
    gui.configure_traits(filename=paramfile)

if __name__ == "__main__":
    main()
