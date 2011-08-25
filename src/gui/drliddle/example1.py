from enthought.traits.api import HasTraits,Int,Float,Str,Property

class Person(HasTraits):
   name = Str
   age = Int
   height = Float
   weight = Float

p = Person(name="Billy",age=18,height=2.,weight=90)
#p.height = "Raspberries"   #As height expects a float, this gives an error
p.configure_traits()

print p.name,p.age,p.height,p.weight

