#!/usr/bin/env python

'''
superclass of modules supporting different file formats
'''

import os


formats = None      # dict: file format support classes, by format class name
ext_xref = None     # dict: cross-reference from extension to format class name


class FileIO(object):
    '''superclass of file format support'''
    
    fileio_kind = 'FileIO'  # internal signature to recognize subclasses
    description = None
    extensions = []
    info = None             # instance of jldesmear.api.info.Info
    
    def __str__(self):
        if self.description is None:
            txt = ''
        else:
            txt = self.description + ' ('
            txt += ' '.join(self.extensions)
            txt += ')'
        return txt
    
    def read(self, filename):
        raise NotImplementedError, "must implement read() method in each subclass"
    
    def save(self, filename):
        raise NotImplementedError, "must implement save() method in each subclass"
    
    def read_SMR(self, filename):
        raise NotImplementedError, "must implement read_SMR() method in each subclass"
    
    def save_DSM(self, filename):
        raise NotImplementedError, "must implement save_DSM() method in each subclass"


def discover_support():
    '''
    return a dictionary of the available file formats
    
    Support modules must be in a file in 
    the **jl_api** directory package in the source tree
    and begin with the prefix ``fileio_``.
    '''
    global formats, ext_xref
    if formats is None:
        owd = os.getcwd()
        path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(path)
        formats = {}
        prefix = 'fileio_'
        ext = '.py'
        for filename in os.listdir('.'):
            if filename.startswith(prefix) and filename.endswith(ext):
                modulename = os.path.splitext(filename)[0]
                if modulename in ('__init__', 'fileio', ):
                    continue
                exec 'import ' + modulename
                contents = locals()[modulename].__dict__
                for key, value in contents.items():
                    if isinstance(value, type) and 'fileio_kind' in dir(value):
                        if key in ('FileIO', ):
                            continue    # do not include the superclass
                        if key in formats:
                            msg = 'Duplicate file format defined: ' + key 
                            msg += ' in ' + filename
                            raise RuntimeError, msg
                        formats[key] = value
                        continue
        os.chdir(owd)
        
        ext_xref = {}
        for fmt in formats:
            obj = formats[fmt]()
            for item in obj.extensions:
                ext = os.path.splitext(item)[1]
                ext_xref[ext] = fmt
    return formats


def makeFilters():
    support = discover_support()
    filters = [str(cls()) for cls in support.values()]
    filters = ';;'.join(filters)
    return filters


discover_support()  # automatically initialize


def main():
    global formats
    formats = discover_support()
    for key, cls in formats.items():
        obj = cls()
        print key, str(obj)
    import pprint
    pprint.pprint(formats)
    pprint.pprint(ext_xref)
    print makeFilters()


if __name__ == "__main__":
    main()
