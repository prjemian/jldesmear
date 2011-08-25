from enthought.traits.api import HasTraits,Int,Float,Str,Property
from enthought.traits.ui.api import View,Item,Label
from enthought.traits.ui.menu import OKButton, CancelButton,RevertButton

class Person(HasTraits):
   name = Str
   age = Int
   height = Float
   weight = Float

   bmi = Property(Float,depends_on=["height","weight"])

   view = View(
               Item("height",label = "Height / m"),
               Item("weight",label = "Weight / kg"),
               Item("bmi"),
               buttons=[RevertButton,OKButton,CancelButton],
              )

   def _get_bmi(self):
      return self.weight/self.height**2

p = Person(name="Billy",age=18,height=2.,weight=90)
#p.height = "Raspberries"   #As height expects a float, this gives an error
p.configure_traits()

print p.name,p.age,p.height,p.weight

