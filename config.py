# -*- coding: utf-8 -*-
#
# Copyright (c) 2008, 2009 Xigital Solutions
#
# Written by Jim Zhan <jim@xigital.com>
#
# This file is part of SFDC-Python Salesforce python accessor.
#
from os.path import abspath, dirname, join
from ConfigParser import ConfigParser
from util import Record


_config = ConfigParser()
# make the options case-sensitive
_config.optionxform = str
_config.read(abspath(
    join(dirname(__file__), 'etc', 'salesforce.conf')
))


def construct(array):
    d = {}
    for key, value in array:
        if not value:
            d[key] = '""'
        elif value.lower() in ('true', 'yes'):
            d[key] = True
        elif value.lower() in ('false', 'no'):
            d[key] = False
        elif value.isdigit():
            d[key] = int(value)
        else:
            d[key] = value
    return Record(**d)

sfdc = construct(_config.items('sfdc'))
http = construct(_config.items('http'))
header = dict(_config.items('header'))
namespace = construct(_config.items('namespace'))


if __name__ == '__main__':
    pass
