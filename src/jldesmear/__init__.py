'''
JLdesmear: iterative desmearing of small-angle scattering data
'''

__project__     = u'JLdesmear'
__author__      = u'Pete R Jemian'
__email__       = u'prjemian@gmail.com'
__copyright__   = u'2013, ' + __author__
__version__     = u'2013-12'
__release__     = __version__ + u'.dev'
__url__         = u'tba'
__description__ = u'Desmear small-angle scattering data by Jemian and Lake'
__long_description__ = __description__ + u'''\n
Iterative desmearing of SAS data using the technique of JA Lake
as implemented by PR Jemian.
'''
__license__     = u' (see LICENSE file for details)'	# consider Creative-Commons


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

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
