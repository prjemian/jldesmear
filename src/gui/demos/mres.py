#!/Users/kpetersn/bin/epd

from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.menu import OKButton,CancelButton

class mresCalc(HasTraits):
	""" MRES calc """

	srev = Float(400.0)
	urev = Float(2.0)

	mres = Property(Float, depends_on=["srev","urev"])

	view = View(
		Item("srev", label="Steps per revolution"),
		Item("urev", label="Units per revolution"),
		Item("mres"),
		buttons=[OKButton, CancelButton],
		)

	def _get_mres(self):
		print self.urev, self.srev
		try:
			retVal = (self.urev / self.srev)
			print "Calculating mres..."
		except ZeroDivisionError:
			retVal = 0
			print "Division by zero!"
		return retVal


if __name__ == "__main__":
	calc = mresCalc()
	calc.configure_traits()

