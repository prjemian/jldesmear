.. $Id$

Change History
==================

development: lake-python (trunk)
------------------------------------------------

Changes:

* refactored :mod:`lake.desmear` into a class: :class:`lake.desmear.Desmearing`

  * allows iterating one at a time
  * computes ChiSqr data after iteration
  * keeps record of all ChiSqr values

* added single iteration method to :mod:`lake.desmear`
* added single and N desmearing iteration controls to GUI
* update plots in the GUI after each iteration by running desmear calculation in a separate thread
* provided ChiSqr v iteration plot (log-lin)

TODO:

#. switch code from [float] to numpy.ndarray
#. add capability for GUI to write desmeared data to a file
#. read data from CanSAS XML
#. read data from HDF5/NeXus

2013-12-22: lake-python-2011-09-traits
------------------------------------------------

Tag existing work and switch GUI to use PySide

2011-08-25: lake-python-2011-08
------------------------------------------------

Initial release:

* python code fully operable
* command line interface

  * uses same paradigm as original FORTRAN code
  * Q&A in a console session, then desmear
  * tested on Windows, Macintosh, and Linux
  * only uses standard Python libraries, no NumPy or SciPy

* All test data copied from legacy C and FORTRAN projects

* Documentation 

  * as good or better than FORTRAN manual
  * could improve still with content from thesis

* graphical user interface

  * provisional, demo only
  * uses Enthought's Traits and Chaco
  * does not write desmeared data to a file
