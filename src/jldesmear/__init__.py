'''
JLdesmear: iterative desmearing of small-angle scattering data
'''

__project__     = u'jldesmear'
__author__      = u'Pete R Jemian'
__email__       = u'prjemian@gmail.com'
__copyright__   = u'2013-2015, ' + __author__
__version__     = u'2015.0530.0'
__release__     = __version__
__url__         = u'http://prjemian.github.io/jldesmear'
__description__ = u'Desmear small-angle scattering data by Jemian and Lake'
__long_description__ = __description__ + u'''\n
Iterative desmearing of SAS data using the technique of JA Lake
as implemented by PR Jemian.
'''
__license__     = u' (see LICENSE file for details)'
__keywords__    = u'small-angle desmearing'
__install_requires__ = ['Sphinx>=0.6', 
                        'numpy>=1.9', 
                        'numpy.ma>=1.0', 
                        'scipy', 
                        'scipy.interpolate',
#                         'matplotlib',
                        ]
__console_scripts__ = [
                       'jldsmear = jldesmear.jldesmear:desmear_cli', 
                       'jldsmear_gui = jldsmear = jldsmear.jldesmear:desmear_gui', 
                       ]


def __about__():
    '''concise description for an about box or other'''
    m = [__project__ + ', release: ' + __release__, ]
    m.append(' ')
    m.append(__author__ + ' <' + __email__ + '>')
    m.append('Copyright (c) ' + __copyright__)
    m.append(' ')
    m.append(__long_description__)
    m.append('For more details, see: ' + __url__)
    return '\n'.join(m)
