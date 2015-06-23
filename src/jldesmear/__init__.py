'''
JLdesmear: iterative desmearing of small-angle scattering data
'''

__project__     = u'jldesmear'
__author__      = u'Pete R Jemian'
__email__       = u'prjemian@gmail.com'
__copyright__   = u'2013-2015, ' + __author__
__version__     = u'2015.0623.1'
__release__     = __version__
__url__         = u'http://jldesmear.readthedocs.org'
__description__ = u'Desmear small-angle scattering data by Jemian and Lake'
__long_description__ = __description__ + u'''\n
Iterative desmearing of SAS data using the technique of JA Lake
as implemented by PR Jemian.
'''
__license__     = u' (see LICENSE file for details)'
__keywords__    = [u'small-angle', 'desmearing', ]
__install_requires__ = ['Sphinx>=0.6', 
                        'numpy>=1.9', 
                        'numpy.ma>=1.0', 
                        'scipy',        # ?>=0.15.1?
                        ]
__console_scripts__ = [
                       'jldsmear = jldesmear.ui:desmear_cli', 
                       'jldsmear_gui = jldsmear.ui:desmear_gui', 
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
