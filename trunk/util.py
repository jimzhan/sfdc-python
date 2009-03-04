# -*- coding: utf-8 -*-
#
# Copyright (c) 2008, 2009 Xigital Solutions
#
# Written by Jim Zhan <jim@xigital.com>
#
# This file is part of SFDC-Python Salesforce python accessor.
#
import re
from os.path import abspath, join, dirname
sfdcIdRegx = re.compile(r'')
dateRegx = re.compile(r'^(\d{4})(.{1})(\d{2})(.{1})(\d{2})$')
datetimeRegx = re.compile(r'^(\d{4}-\d{2}-\d{2})(.{1})(\d{2}:\d{2}:\d{2})$')


here = lambda: abspath(join(dirname(__file__), '..'))

def getName():
    ''' sys._getframe() returns the current frame object.
        f_back is a link to the frame object one high in the stack,
        which is the frame object of the calling function.
        f_code is an object which basically describes the function related
        to the current frame. co_name is the name of the function.
    
        NOTE I'm fairly sure this *isn't* a documented interface,
             (the '_' pretty much indicates that), so it might not
             work in other implementation of python or future versions of python.
    '''
    import sys
    return sys._getframe().f_back.f_code.co_name


def getTime(timestamp):
    """ Turn standard timestamp(2009-02-25T10:35:13.959Z)
        into datetime.
    """
    from datetime import datetime
    date, time = timestamp.split('T')
    year, month, day = [int(item) for item in date.split('-')]
    time = time.replace('Z', '').split(':')
    hour, minute = int(time[0]), int(time[1])
    second, microsecond = time[-1].split('.')
    
    return datetime(
        year,
        month,
        day,
        hour,
        minute,
        int(second),
        int(microsecond)
    )


class Record(object):
    def __init__(self, **args):
        self.__dict__.update(args)


class Singleton(type):
    '''Independent Singleton class.
        Usage:
            Class Connection:
                __metaclass__ = Singleton
    '''
    def __call__(cls, *args, **kw):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance
    

if __name__ == '__main__':
    print method()
