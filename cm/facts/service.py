# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service host
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class Service(BaseFact):
    ATTRS = ["name", "enabled", "version", "port"]
    ID = ["name"]

    def __init__(self, name, enabled=False, version=None, port=None):
        super(Service, self).__init__()
        self.name = name
        self.enabled = enabled
        self.version = version
        self.port = port

    def __unicode__(self):
        return "Service %s" % self.name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value or None

    @property
    def enabled(self):
        return self._enabled
    
    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value)

    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, value):
        self._version = value

    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self, value):
        self._port = value
