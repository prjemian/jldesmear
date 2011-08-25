from enthought.traits.api import HasTraits,Int,Float,Str,Property,Range,Array
from enthought.traits.ui.api import View,Item,Label
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from numpy import array,poly1d,arange,linspace

class PlotterApplication(HasTraits):
   x0 = Range(-5.,5.)
   c0 = Range(-5.,5.)
   c1 = Range(-5.,5.)
   c2 = Range(-5.,5.)

   xdata = Array
   ydata = Property(Array,depends_on=["x0","c0","c1","c2"])

   #Set the coeffients to 0 as default
   def _x0_default(self): return 0.
   def _c0_default(self): return 0.
   def _c1_default(self): return 0.
   def _c2_default(self): return 0.

   def _xdata_default(self): return linspace(-10,10,100)

   def _get_ydata(self):
      poly = poly1d([self.c2,self.c1,self.c0])
      return poly(self.xdata-self.x0)

   traits_view = View(
                  ChacoPlotItem("xdata","ydata", y_bounds=(-10.,10.),y_auto=False,resizable=True,show_label=False,x_label="x",y_label="y",title=""),
                  Item('x0'),
                  Item('c0'),
                  Item('c1'),
                  Item('c2'),
                  resizable = True,
                  width=900, height=800,
                  title="Plot App"
                     )

if __name__ == "__main__":
   p = PlotterApplication()
   p.configure_traits()
