#!/usr/bin/env python

'''
Enthought's chaco tutorial 1

Obtained by google search: ``enthought traits tutorial1 full code``
from Sphinx source code file.

:see: https://svn.enthought.com/svn/enthought/Chaco/trunk/docs/source/user_manual/tutorial_1.rst
'''


########### SVN repository information ###################
# $Date: 2011-08-27 12:34:12 -0500 (Sat, 27 Aug 2011) $
# $Author: jemian $
# $Revision: 1694 $
# $URL: http://svn.jemian.org/svn/regitte/lake-python/trunk/src/gui/demos/chaco_tutorial1.py $
# $Id: chaco_tutorial1.py 1694 2011-08-27 17:34:12Z jemian $
########### SVN repository information ###################

from enthought.traits.api import HasTraits, Instance, Int, Button, String, Range
from enthought.traits.ui.api import View, Group, Item, StatusItem
from enthought.enable.api import ColorTrait
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.api import marker_trait, Plot, ArrayPlotData
from enthought.chaco.tools.pan_tool import PanTool
from enthought.chaco.tools.zoom_tool import ZoomTool
from numpy import linspace, sin

class ScatterPlotTraits(HasTraits):

	plot = Instance(Plot)
	color = ColorTrait("blue")
	marker = marker_trait
	marker_size = Range(2, 50, 5)

	btnChange = Button('* -1')
	status_msg = String
	status_label = String('status:')
	status_bar = [
		StatusItem(name = 'status_label', width = 80),
		StatusItem(name = 'status_msg', width = 0.5),
	]

	traits_view = View(
		Group(
			Item('color', label="Color", style="custom"),
			Item('marker', label="Marker"),
			Item('marker_size', label="Size"),
			Item('plot', editor=ComponentEditor(), show_label=False),
			Item('btnChange', show_label=False),
			orientation = "vertical"
		),
		width=800, height=600, 
		resizable=True,
		title="Chaco Plot",
		statusbar = status_bar,
	)

	def __init__(self):
		super(ScatterPlotTraits, self).__init__()
		x = linspace(-14, 14, 100)
		y = sin(x) * x**3
		plotdata = ArrayPlotData(x = x, y = y)
		plot = Plot(plotdata)

		plot.tools.append(PanTool(plot))
		plot.tools.append(ZoomTool(plot))

		self.renderer = plot.plot(("x", "y"), type="scatter", color="blue")[0]
		self.plot = plot
		self.status_msg = "init complete"

	def _color_changed(self):
		self.renderer.color = self.color
		self.status_msg = "new color: " + str(self.color)

	def _marker_changed(self):
		self.renderer.marker = self.marker
		self.status_msg = "new marker: " + str(self.marker)

	def _marker_size_changed(self):
		self.renderer.marker_size = self.marker_size
		self.status_msg = "new marker size: " + str(self.marker_size)

	def _btnChange_fired(self):
		''' change data '''
		self.status_msg = "multiply data by -1"
		pd = self.plot.data
		pd.set_data("y", -pd.get_data("y") )

if __name__ == "__main__":
	ScatterPlotTraits().configure_traits()
