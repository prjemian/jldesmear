'''
Created on Dec 26, 2012

@author: Pete
'''

class Foo(object):

    def get_children(self):
        return vars()
        return [cls for cls in vars()['Foo'].__subclasses__()]


class Bar(Foo): pass
class Baz(Foo): pass
class Bing(Bar): pass

print([cls.__name__ for cls in vars()['Foo'].__subclasses__()])

print([cls for cls in vars()['Foo'].__subclasses__()])

for cls in vars()['Foo'].__subclasses__():
    print(cls.__base__)

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]

print(all_subclasses(vars()['Foo']))

foo = Foo()
print "-"*40
print foo.get_children()
