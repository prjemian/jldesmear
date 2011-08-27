#!/usr/bin/env python

''' demo the menu bar

:see: https://mail.enthought.com/pipermail/enthought-dev/2010-February/025563.html
'''


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


from enthought.pyface.action.api \
    import Group as ActionGroup 

from enthought.traits.api \
    import HasTraits, Int, Str, Button

from enthought.traits.ui.api \
    import Handler, View, Item, StatusItem

from enthought.traits.ui.menu \
    import Action, Menu, MenuBar, CloseAction, Separator


class MyHandler(Handler): 
    def increment(self, info): 
        my_view = info.ui.context['object'] 
	my_view.value += 1

class MyView(HasTraits):
    value = Int(0)
    status_msg = Str
    status_label = Str('status:')
    btnIncrement = Button("+1")

    def _btnIncrement_fired(self):
        pass

    def trait_view(self, parent=None):
        menu_file = Menu(
	    Separator(),
	    CloseAction,
	    name='File'
	)
        menu_action = Menu(
	    Action(
              name='I&ncrement Value', 
	      action='increment'
            ), 
	    name='Actions'
	)
        menu_bar = MenuBar(
	    menu_file, 
	    menu_action
	)

        return View(
            Item('value'),
            handler=MyHandler(),
            menubar=menu_bar,
            height=200,
            width=400,
            title="MenuBar demo",
            buttons = ['Ok', 'Cancel'],
            statusbar = [
                StatusItem(name = 'status_label', width = 80),
                StatusItem(name = 'status_msg', width = 0.5),
            ]
        )

MyView().configure_traits() 
