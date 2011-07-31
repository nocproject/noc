# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Datasource interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.settings import INSTALLED_APPS


datasource_registry = {}


class DataSourceBase(type):
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        if m._name:
            datasource_registry[m._name] = m
        return m


class DataSource(object):
    __metaclass__ = DataSourceBase
    _name = None

    def __init__(self, **kwargs):
        self._data = None

    @property
    def _is_empty(self):
        return self._data is None


## Load datasources
for app in INSTALLED_APPS:
    if app.startswith("noc."):
        if os.path.exists(os.path.join(app[4:], "datasources.py")):
            __import__(app + ".datasources", {}, {}, "*")
