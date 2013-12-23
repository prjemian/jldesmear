
'''
Simple management of user input for lake desmearing.
Uses Enthought's Chaco package.
Reads the various parameters from a pickled file prepared 
via Traits or falls back to the default set if the pickled file
is not found.

:note: 
    Cannot have Traits put up GUI for user input
    *AND* then have Chaco put up GUI with plots. 
    Dismissing the Traits GUI kills the wx event loop.

The Traits GUI 
(selected with ``allow_traits_gui = True``)
will collect user input and save it in a
parameters file, ``only_traits.pkl``, then run the desmearing.

The Chaco GUI 
(selected with ``allow_traits_gui = False``)
will read the parameters file, ``only_chaco.pkl``, 
if it is present, then run the desmearing and then put
up a line chart GUI with the plotted smeared and desmeared curves.

The parameters file is located in the same directory as this file.
It is pickled and is not easily readable but is easy for reading
and writing by Traits.

Goal:

Learn how to have both Traits and Chaco work together.
See the tutorial for more help::

* http://github.enthought.com/chaco/user_manual/tutorial_1.html#tutorial-1
* http://github.enthought.com/chaco/user_manual/tutorial.html
* http://github.enthought.com/chaco/quickstart.html#chaco-plot-integrated-in-a-traits-application
* http://code.enthought.com/projects/chaco/gallery.php

Basic Idea:

* select data for desmearing
* plot that data
* select desmearing range and terms (graphically, if possible, text at first)
* show effect of various terms on plot
* do desmearing on demand
* show the residuals plots in real time
* save desmeared data on demand

'''

