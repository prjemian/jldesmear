Forward Smearing
################

Some instruments designed to measure small-angle scattering
have intrinsic *slit-smearing* of the in their design.  One 
such example is the Bonse-Hart design which uses single
crystals to collimate the beam incident on the sample as well
as to collimate the scattered beam beam that will reach the
detector.

 .. _fig.smearing:

 .. figure:: smearing.png
     :alt: fig.smearing
     :width: 60%

     Slit smearing geometry of the Bonse-Hart design.

Source Code Documentation
=========================

.. automodule:: jldesmear.jl_api.smear
    :members: 
    :synopsis: :mod:`~jldesmear.jl_api.smear` is used by :mod:`~jldesmear.jl_api.desmear` to forward smear a test case.
