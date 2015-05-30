Command-line program for Jemian/Lake desmearing
###############################################

:mod:`jldesmear.api.traditional` is the main program to run desmearing.
It provides the same command-line interface as its FORTRAN and C predecessors.
The main command-line interface is started with a Python command such as::

	import jldesmear.api
	jldesmear.api.traditional.command_line_interface()

Example
*******

.. toctree::
   :maxdepth: 2
   
   example

Supporting Code Modules
***********************

No support code modules contain GUI code of any sort.
Any output from these modules, if at all, is directly to the console. 

.. toctree::
   :maxdepth: 2
   
   info
   desmear
   smear
   extrapolations
   StatsReg
   textplots
   toolbox


:mod:`~jldesmear.jl_api.traditional` documentation
**************************************************

.. automodule:: jldesmear.jl_api.traditional
    :members: 
    :synopsis: command-line program to run desmearing
