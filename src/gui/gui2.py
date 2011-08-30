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
#os.environ['ETS_TOOLKIT'] = 'qt4'

import time

import lake.toolbox
import lake.desmear
import lake.info

from enthought.traits.api \
    import HasTraits, Instance, Int, File, String, Float, Enum, Button, Range

from enthought.traits.ui.api \
    import View, Group, Item, StatusItem, NoButtons, HSplit, VSplit, HGroup, spring

from enthought.enable.component_editor \
    import ComponentEditor

from enthought.chaco.api \
    import Plot, ArrayPlotData, ScatterPlot

from enthought.chaco.tools.api \
    import PanTool, ZoomTool


class Gui2(HasTraits):
    '''Provide interactive access to all the parameters used in desmearing
    
    This is a main GUI for the Lake/Jemian small-angle scattering desmearing program.  
    It uses Traits, Chaco, and Enable.  
    Call it with code like this::

        Gui2().configure_traits()

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
        statusbar = [
            StatusItem(name = 'status_label', width = 80),
            StatusItem(name = 'status_msg', width = 0.5),
        ],
        buttons=NoButtons,
    )

    def __init__(self):
        super(Gui2, self).__init__()
        self.sas_plot, self.sas_renderer = self._init_plot("goldenrod")
        self.residuals_plot, self.residuals_renderer = self._init_plot("silver")

    def _infile_default(self): return os.path.join('..', '..', 'data', 'test1.smr')
    def _l_o_default(self): return 0.08
    def _qFinal_default(self): return 0.08
    def _NumItr_default(self): return 10
    def _extrapolation_default(self): return 'linear'
    def _LakeWeighting_default(self): return 'fast'
    
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
        # avoid extra calls to _console_text_changed(), assign only once
        self.console_text = txt

    def _btnClearConsole_fired(self):
        ''' clear the console widget '''
        self.console_text = ""
        self.SetStatus('console cleared')

    def _btnRestartDsm_fired(self):
        self.SetStatus('desmearing reset')
        self._infile_changed()

    def _btnDesmear_fired(self):
        self.SetStatus('desmearing %d times' % self.NumItr)
        if self.obj_dsm:
            self.toInfo(self.obj_dsm.params)
            for _ in range(self.NumItr):
                self.obj_dsm.iteration()
                self.dsm_callback(self.obj_dsm)


    def _btnDesmearOnce_fired(self):
        self.SetStatus('desmearing should go one iteration')
        if self.obj_dsm:
            self.toInfo(self.obj_dsm.params)
            self.obj_dsm.iteration()
            self.dsm_callback(self.obj_dsm)

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
        ''' copy local variables to Info() structure '''
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

        d = self.residuals_plot.data
        d.set_data("x", dsm.q)
        d.set_data("y", dsm.z)
        
        # force the plot to redraw itself
        r = self.residuals_plot
        #r.invalidate_and_redraw()
        r.request_redraw()
        # TODO: plot should update
        time.sleep(0.05)

        self.SetStatus( msg )


if __name__ == "__main__":
    Gui2().configure_traits()
