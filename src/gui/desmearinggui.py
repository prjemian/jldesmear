#!/usr/bin/env python

'''
Lake desmearing GUI using Enthought's Traits, Chaco, and Enable packages.

:note:  If you are using Ubuntu 11.04 and cannot see a menubar,
   this is a bug in Ubuntu 11.04. Try setting the environment
   variable: UBUNTU_MENUPROXY=1

   Or, the code does not call for a menubar. ... Nevermind.
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
#os.environ['ETS_TOOLKIT'] = 'qt4'
os.environ['UBUNTU_MENUPROXY'] = "1"    # work around a menubar bug in Ubuntu 11.04

import threading

import lake.toolbox
import lake.desmear
import lake.info

from enthought.traits.api \
    import HasTraits, Instance, File, String, Float, Enum, Button, Range

from enthought.traits.ui.api \
    import View, Group, Item, StatusItem, NoButtons, HSplit, VSplit, HGroup, spring
    
from enthought.traits.ui.menu import StandardMenuBar

from enthought.enable.component_editor \
    import ComponentEditor

from enthought.chaco.api \
    import Plot, ArrayPlotData, ScatterPlot

from enthought.chaco.tools.api \
    import PanTool, ZoomTool



class ChiSqr_plot(HasTraits):
    ''' '''
    plot = Instance(Plot)
    renderer = Instance(ScatterPlot)

    def __init__(self):
        plot = Plot( ArrayPlotData(x = [], y = []) )
        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.overlays.append(ZoomTool(plot))
        r = plot.plot(
            ("x", "y"), 
            type="scatter", 
            color="goldenrod", 
            marker='circle', 
            marker_size=3
        )
        self.plot = plot
        self.renderer = r[0]  # 1st item in the list is our scatter plot

    def SetData(self, chiSqr):
        '''
        provide the data to be plotted,
        replaces any existing data on the plot
        
        :param [float] chiSqr: list of ChiSqr values for each iteration
        '''
        it = range(len(chiSqr))
        p = self.plot
        d = p.data
        d.set_data("x", it)
        d.set_data("y", chiSqr)
        p.index_scale = 'linear'
        p.value_scale = 'log'
    
    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False),
        resizable = True,
        title="ChiSqr vs. desmearing iteration",
        width=400,
        height=300,
    )


class DesmearingGui(HasTraits):
    '''Provide interactive access to all the parameters used in desmearing
    
    This is a main GUI for the Lake/Jemian small-angle scattering desmearing program.  
    It uses Traits, Chaco, and Enable.  
    Call it with code like this::

        DesmearingGui().configure_traits()

    '''
    infile = File(label="I(Q) file", desc="the name of the input smeared SAS data file", )
    sas_plot = Instance(Plot)
    residuals_plot = Instance(Plot)
    sas_renderer = Instance(ScatterPlot)
    residuals_renderer = Instance(ScatterPlot)
    status_label = String('status:')
    status_msg = String
    obj_dsm = Instance( lake.desmear.Desmearing )
    btnRestartDsm = Button("(re)start")
    btnDesmear = Button("N times")
    btnDesmearOnce = Button("once")
    btnClearConsole = Button("clear console")
    console_text = String
    chiSqr_plot = Instance(ChiSqr_plot)

    l_o = Float(label="slit length", desc="slit length, as defined by Lake", )
    qFinal = Float(label="qFinal", desc="fit extrapolation constants for Q>=qFinal",)
    NumItr = Range(1,1000, 10, label="# iterations", desc="number of desmearing iterations",)
    extrapolation = Enum( 
                 'constant',  'linear', 'powerlaw', 'Porod',
                 label="Extrapolation", desc="form of extrapolation",)
    LakeWeighting = Enum( 
                 'constant', 'fast',  'ChiSqr',
                 label="weighting", desc="weighting method for iterative refinement",)

    sas_plot_item = Item('sas_plot', editor=ComponentEditor(), show_label=False)
    residuals_plot_item = Item('residuals_plot', editor=ComponentEditor(), show_label=False)

    console_item = Item(
        "console_text", 
        springy=True, 
        style='custom', 
        show_label=False, 
    )
    
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
                    Item('btnDesmearOnce', show_label=False),
                    Item('btnRestartDsm', show_label=False),
                    spring,
                    Item('chiSqr_plot', show_label=False),
                    label="desmearing controls",
                    show_border = True,
                ),
                Group(
                    console_item,
                    Item('btnClearConsole', show_label=False),
                    label="console output",
                    show_border = True,
                ),
            ),
            VSplit(
                sas_plot_item,
                residuals_plot_item,
            ),
        ),
        resizable = True,
        title="Lake/Jemian Desmearing GUI",
        width=700,
        height=500,
        menubar = StandardMenuBar,
        statusbar = [
            StatusItem(name = 'status_label', width = 80),
            StatusItem(name = 'status_msg', width = 0.5),
        ],
        buttons=NoButtons,
    )

    def __init__(self):
        super(DesmearingGui, self).__init__()
        self.sas_plot, self.sas_renderer = self._init_plot("goldenrod")
        self.residuals_plot, self.residuals_renderer = self._init_plot("silver")
        if self.chiSqr_plot == None:
            self.chiSqr_plot = ChiSqr_plot()

    def _infile_default(self): return os.path.join('..', '..', 'data', 'test1.smr')
    def _l_o_default(self): return 0.08
    def _qFinal_default(self): return 0.08
    def _NumItr_default(self): return 10
    def _extrapolation_default(self): return 'linear'
    def _LakeWeighting_default(self): return 'fast'
    def _console_text_default(self): return ''
    
    def _init_plot(self, color = "blue"):
        '''common construction of a plot
        
        :return: tuple of objects of plot and its renderer
        :rtype: (object, object)
        '''
        plot = Plot( ArrayPlotData(x = [], y = []) )
        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.overlays.append(ZoomTool(plot))
        r = plot.plot(
            ("x", "y"), 
            type="scatter", 
            color=color, 
            marker='circle', 
            marker_size=3
        )
        renderer = r[0]  # 1st item in the list is our scatter plot
        return plot, renderer

    def _infile_changed(self):
        if os.path.exists(self.infile):
            Qvec, smr, esd = lake.toolbox.GetDat(self.infile)
            p = self.sas_plot
            d = p.data
            d.set_data("x", Qvec)
            d.set_data("y", smr)
            p.index_scale = 'log'
            p.value_scale = 'log'
            
            # TODO: append dsm and resmeared data curves
            # TODO: what about error bars?
            
            p = self.residuals_plot
            p.data.set_data("x", Qvec)
            p.index_scale = 'log'
            p.value_scale = 'linear'
            self.SetStatus("read %d points from %s" % (len(Qvec), self.infile) )
            self.setupDesmearing(Qvec, smr, esd)
        else:
            self.SetStatus("could not find " + self.infile)

    def _status_msg_changed(self):
        txt = ""
        if len(self.console_text):
            txt = self.console_text + "\n"
        txt += self.status_msg
        self.console_text = txt     # assign only once to avoid excess Traits updates

    def _btnClearConsole_fired(self):
        ''' clear the console widget '''
        self.console_text = ""
        self.SetStatus('console cleared')

    def _btnRestartDsm_fired(self):
        self.SetStatus('desmearing reset')
        self._infile_changed()

    def _btnDesmear_fired(self):
        self.SetStatus('desmearing %d iterations' % self.NumItr)
        if self.obj_dsm:
            self.toInfo(self.obj_dsm.params)
            IterativeDesmear(self.obj_dsm, self.NumItr).start()

    def _btnDesmearOnce_fired(self):
        self.SetStatus('desmearing one iteration')
        if self.obj_dsm:
            self.toInfo(self.obj_dsm.params)
            IterativeDesmear(self.obj_dsm, 1).start()

    def SetStatus(self, msg):
        ''' put text in the status box '''
        self.status_msg = msg
    
    def setupDesmearing(self, Qvec, smr, esd):
        ''' prepare to start desmearing '''
        if len(Qvec) == 0:
            self.SetStatus("cannot desmear now, no data")
            return
        if len(Qvec) != len(smr):
            self.SetStatus("cannot desmear now, number of data points inconsistent")
            return
        if len(Qvec) != len(esd):
            self.SetStatus("cannot desmear now, number of data points inconsistent")
            return
        if self.qFinal > Qvec[-2]:
            self.SetStatus("cannot desmear now, fit range beyond data range")
            return

        params = lake.info.Info()
        if params == None:
            raise Exception, "Could not create Info() structure ... serious!"
        self.toInfo(params)
        self.obj_dsm = lake.desmear.Desmearing(Qvec, smr, esd, params)
        self.dsm_callback(self.obj_dsm)
        
    def toInfo(self, params):
        ''' copy local variables to Info() structure 
        
        :param params: desmearing parameters structure
        :type params: Info object
        '''
        params.infile = self.infile
        #params.outfile = self.outfile
        params.slitlength = self.l_o
        params.sFinal = self.qFinal
        params.NumItr = self.NumItr
        params.extrapname = self.extrapolation
        params.LakeWeighting = self.LakeWeighting
        params.callback = self.dsm_callback
        
    def dsm_callback(self, dsm):
        '''
        this function is called after every desmearing iteration
        from :func:`lake.desmear.Desmearing.traditional()`
    
        :param obj dsm: desmearing parameters object
        :return: should desmearing stop?
        :rtype: bool
        '''
        msg = "#" + str(dsm.iteration_count)
        msg += "  ChiSqr=" + str(dsm.ChiSqr[-1])
        msg += "  " + str(dsm.params.extrap)
        
        # TODO: update the SAS plot

        d = self.residuals_plot.data
        d.set_data("x", dsm.q)
        d.set_data("y", dsm.z)
        
        self.chiSqr_plot.SetData(dsm.ChiSqr)

        self.SetStatus( msg )


class IterativeDesmear(threading.Thread):
    ''' 
    Run ``n`` iterations of the desmearing operation in a separate thread.
    Running in a separate thread with callbacks allows the 
    GUI widgets to be updated after each iteration.
        
    :param obj dsm: Desmearing object
    :param int n: number of iterations to perform
    
    Start this thread with code such as this example::
    
        IterativeDesmear(self.obj_dsm, self.NumItr).start()

    '''
    
    def __init__(self, dsm, n):
        threading.Thread.__init__(self)
        self.dsm = dsm
        self.n = n

    def run(self):
        for _ in range(self.n):
            self.dsm.iterate_and_callback()


if __name__ == "__main__":
    DesmearingGui().configure_traits()
