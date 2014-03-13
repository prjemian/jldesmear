------------------------------------
Example using ``test1.smr`` data set
------------------------------------

Input Commands
--------------

.. see :func:`jldesmear.api.smear.Plengt` for an example of formatted math

.. needs graphviz
.. .. inheritance-diagram:: jldesmear.api.traditional jldesmear.api.smear jldesmear.api.StatsReg jldesmear.api.textplots

Start the program from the ``data`` directory in the source tree.
We'll use UNIX shell redirection to get everything in a text file::

	cd src/jldesmear/data
	python ../api/traditional.py < test1.inp > test1.out

The program will print a header::

	<<< 	SAS data desmearing, by Pete R. Jemian
	<<< 	Based on the iterative technique of JA Lake and PR Jemian.
	<<< 	P.R.Jemian,; Ph.D. thesis, Northwestern University (1990).
	<<< 	J.A. Lake; ACTA CRYST 23 (1967) 191-194.
	<<< 
	<<< 	$Id$
	<<< 	desmear using the same FORTRAN & C command line interface
	<<< 

Then, the program will ask some questions about the input data.
Here, the test data is ``test1.smr``::

	<<< What is the input data file name? <''=Quit> <> ==>  
	>>> test1.smr

Name the (new) file name to write the results.  If it exists, 
it will be overwritten without further comment.
Here, we choose the name ``test1.out``::

	<<< What is the output data file name? <> ==>  
	>>> test1.out

The slit length is the term *l_o* and has the same units as *X*::

	<<< What is the slit length (x-axis units)? <1.0> ==>  
	>>> .08

To complete the smearing integral at highest *X*, it is necessary
to extrapolate beyond the range of measured data.  
Choose the functional form that best represents the data at 
highest *X*.  Fit coefficients will be evaluated for each
desmearing iteration over the range ``X_start <= X <= X_max``::

	<<< Extrapolation forms to avoid truncation-error.
	<<<    constant = flat background, I(q) = B
	<<<    linear = linear, I(q) = b + q * m
	<<<    powerlaw = power law, I(q) = b * q^m
	<<<    Porod = Porod law, I(q) = Cp + Bkg / q^4
	<<< 

Choose the *linear* form (although *constant* would work with this data as well)::

	<<< Which form? <constant> ==>  
	>>> linear

This is ``X-start`` as noted above: ``.08``::

	<<< What X to begin evaluating extrapolation (x-axis units)? <1.0> ==>  
	>>> .08

Accept the solution after 20 iterations this time::

	<<< How many iteration(s)? (10000 = infinite) <10000> ==>  
	>>> 20

This question is largely historical.  The ``fast`` method 
is **always** the best choice.  The others were implementations of either
Jansson or Halsey & Blass.  They converge more slowly by far.
That said, you are free to re-determine this for yourself.
Press the [return] key to accept the default suggestion::

	<<<  Weighting methods for iterative corrections:
	<<<  Correction = weight * (MeasuredI - SmearedI)
	<<<    constant: weight = 1.0
	<<<    fast: weight = CorrectedI / SmearedI
	<<<    ChiSqr: weight = 2*SQRT(ChiSqr(0) / ChiSqr(i))
	<<< 
	<<< Which method? <fast> ==>
	>>> 


Program output to console
-------------------------

Now the program starts the work of desmearing.  The first step shows
an awful chi-square statistic.  This will improve with subsequent iterations.
The plot is standardized residual vs. data point number.  There are
``==========`` bars indicated at ``+1`` and ``-1``; these merge together 
on the first plot.::

	Input file: test1.smr
	-/|\ ...
	standardized residuals, ChiSqr = 1.29823e+07, iteration=0
	x: min=1   step=3.45833   max=250
	y: min=-545.836   step=24.8717   max=1.34169
	 ------------------------------------------------------------------------- 
	|                                                          +              |
	|==============================================+++++++++++++++++++++++++++|
	|+                                            ++                          |
	|                                            ++                           |
	|                                          ++                             |
	|+                              +        ++                               |
	|++                             +       ++                                |
	|                              +       ++                                 |
	|                            +++      ++                                  |
	|                          +++        +                                   |
	|                        ++          +                                    |
	|                       ++          ++                                    |
	|                      +            +                                     |
	| ++                +++            ++                                     |
	|  ++          +++++               +                                      |
	|   ++++++++++++                   +                                      |
	|                                 +                                       |
	|                                 +                                       |
	|                                 +                                       |
	|                                +                                        |
	|                                +                                        |
	|                                +                                        |
	|                                +                                        |
	 ------------------------------------------------------------------------- 

After the next iteration, the chi-squared statistic has improved by an order 
of magnitude but the plot still does not different::
 
	standardized residuals, ChiSqr = 1.36804e+06, iteration=1
	x: min=1   step=3.45833   max=250
	y: min=-206.354   step=9.44611   max=1.46073
	 ------------------------------------------------------------------------- 
	|                                                          +              |
	|================================================+++++++++++++++++++++++++|
	|+                                             ++                         |
	|                                             ++                          |
	|+                                            +                           |
	| +                             +            +                            |
	|                             +++           ++                            |
	|                         +++++           ++                              |
	|                       +++              ++                               |
	| ++               +++++                ++                                |
	|  ++        +++++++                   ++                                 |
	|  +++++++++++                         +                                  |
	|     +                               +                                   |
	|                                     +                                   |
	|                                    +                                    |
	|                                   ++                                    |
	|                                   +                                     |
	|                                  +                                      |
	|                                  +                                      |
	|                                 +                                       |
	|                                 +                                       |
	|                                +                                        |
	|                                +                                        |
	 ------------------------------------------------------------------------- 
 
Skipping forward a few iterations, we see some real progress::
 
	standardized residuals, ChiSqr = 566.385, iteration=5
	x: min=1   step=3.45833   max=250
	y: min=-3.97891   step=0.499962   max=7.02024
	 ------------------------------------------------------------------------- 
	|  +                                                                      |
	|   +                                                                     |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	| +  +                                   +                                |
	|       +                               + +++                             |
	|                                      +  ++++                            |
	|+     +                              ++++   +                            |
	|++    +                              ++                                  |
	|  +      +  ++                      ++       +                           |
	|=======+===+=+=++=++=+==============+=============+===+===+======+====== |
	| +       ++ +++ + ++ +++++++  +              +    + ++ + ++++++++++++++++|
	|+ +++ + + ++  +++++ + ++++++++++             + + ++++ + ++++++++++++++++ |
	|+ + + ++ + +       ++  +  +  + +   ++          +++ +++++ ++  +           |
	|========+===================++=====+==========+=+++=====+=============== |
	|     +                            +           +++                        |
	|   +                                                                     |
	|        +                         +                                      |
	|                                ++                                       |
	|                                ++                                       |
	 ------------------------------------------------------------------------- 
	 
After about 10 iterations or so, it seems convergence has been achieved.
The chi-squared statistic has dropped and the plot looks more 
randomly-arranged about 0.::
 
	standardized residuals, ChiSqr = 103.479, iteration=11
	x: min=1   step=3.45833   max=250
	y: min=-2.89125   step=0.349475   max=4.7972
	 ------------------------------------------------------------------------- 
	|   +                                                                     |
	|  +                                                                      |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|    +                                                                    |
	|       +                                                                 |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|+                                                                        |
	|=+====+================================================================= |
	|  +   ++ +   +     +                           +  +   +   +              |
	| +      +       +  +   ++ ++ +     + ++      ++ +++ ++ + +               |
	|+ +++   ++++++++++++ ++ +++++ ++++++++++++++ ++++  ++++ +++++++++++++++++|
	|  + ++    +++ ++ ++++ +++++++++ ++     ++++++++ +++++ ++ ++ ++  +  ++++  |
	|++    +  + +                            +  ++     +  +  + +              |
	|====++=+================================================================ |
	|+     +                                                                  |
	|                                                                         |
	|        +                                                                |
	|                                                                         |
	|   +                                                                     |
	 ------------------------------------------------------------------------- 
	 
Finally, after 20 iterations (numbered 0 .. 19)::
 
	standardized residuals, ChiSqr = 46.9362, iteration=19
	x: min=1   step=3.45833   max=250
	y: min=-2.94353   step=0.264922   max=2.88475
	 ------------------------------------------------------------------------- 
	|   +                                                                     |
	|                                                                         |
	|  +                                                                      |
	|                                                                         |
	|    +                                                                    |
	|       +                                                                 |
	|                                                                         |
	|+                                                                        |
	|==+===================================================================== |
	|      + ++                                                               |
	|  +  + ++    +  +  +   ++  + +             +   ++++  +++ ++             +|
	| +  +++  ++++++ ++ + ++ ++++++++++++++++++++++++++++++++++ +++++++++++++ |
	|  ++ +  ++++++ ++++ + +++++++++ + ++ ++++++++++++++++ +++++ + ++ + ++ ++ |
	|++                                              + +  ++ + +              |
	|+     +                                                                  |
	|======+================================================================= |
	|    +  ++                                                                |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|                                                                         |
	|   +                                                                     |
	 ------------------------------------------------------------------------- 

The result is accepted and the data are saved to the output file::

	Saving data in file: test1.out
	SAS log-log plot, final, S=input, D=desmeared
	x: min=-7.898   step=0.0889226   max=-1.49558
	y: min=3.0786   step=0.637599   max=17.1058
	 ------------------------------------------------------------------------- 
	|D                                                                        |
	|DDDDDD                                                                   |
	|D DDDDDDDD                                                               |
	|         DDDDD                                                           |
	|             DDD                                                         |
	|                DDD                                                      |
	|                  DDD                                                    |
	|                     DD                                                  |
	|SSSSS                  DDD                                               |
	|    SSSSSSS              DD                                              |
	|          SSSSS            DDD                                           |
	|               SSSS          DD                                          |
	|                  SSSS        DDD                                        |
	|                      SSS        DD                                      |
	|                         SSS      DDD                                    |
	|                           SSS      DDD                                  |
	|                              SSS     DDD                                |
	|                                SSSS    DDD                              |
	|                                   SSS     DD                            |
	|                                     SSSS   DDDD                         |
	|                                        SSSSS DDDD                       |
	|                                            SSSSSDDDDDDDDDD  D DD DDDDDD |
	|                                                  D DDDDDSSDDDDDDDDDDDDDD|
	 ------------------------------------------------------------------------- 

Data Files
----------

Command Input File (:file:`test1.inp`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../src/jldesmear/data/test1.inp

Input Data File (:file:`test1.smr`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../src/jldesmear/data/test1.smr

Output Data File (:file:`test1.dsm`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../src/jldesmear/data/test1.dsm

Complete Program Output (:file:`test1.out`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Too big for the documentation.  See the source code distribution.

.. .. literalinclude:: ../../data/test1.out

