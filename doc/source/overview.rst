.. $Id$

Overview
########

Desmear 1-D SAXS or SANS data according to the method 
of JA Lake as implemented by Pete Jemian.

This program applies the iterative desmearing technique of Lake
to small-angle scattering data.  The way that the program works
is that the user selects a file of data *(x,y,dy)* to be desmeared.
If a file was not chosen, the program will end.  Otherwise the
user is then asked to specify the slit-length (in the units of the
x-axis); the *x* at which to begin fitting the last data points to a
power-law of *x*, the output file name, and the number of iterations
to be run.  Then the data file is opened, the data is read, and the
data file is closed.  The program begins iterating and shows an
indicator of progress on the screen in text format.

It is important to only provide *smeared* data (data that has not
been desmeared, even partially) to this program as you will see.  
The iterative desmearing technique should be made to iterate
with the original, smeared data and subsequent trial solutions
of desmeared data.

The integration technique used by this program to smear the data
is the trapezoid-rule where the step-size is chosen by the
spacing of the data points themselves.  A linear
interpolation of the data is performed.  To avoid truncation
effects, a power-law extrapolation of the intensity
is made for all values beyond the range of available
data.  This region is also integrated by the trapezoid
rule.  The integration covers the region from ``l = 0``
up to ``l = lo``. (see routine :mod:`jldesmear.api.smear`).
This technique allows the slit-length weighting function
to be changed without regard to the limits of integration
coded into this program.


Input data format
#################

Input data will be provided in an ASCII TEXT file
as three columns *(Q, I, dI)* separated by white space.
Units must be compatible.  (*I* and *dI* must have same units)

:*Q*:   scattering vector (any units)
:*I*:   measured SAS intensity
:*dI*:  estimated uncertainties of *I* (usually standard deviation).
        Note that *dI* **MUST** be provided and **MUST** not be zero.
