# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Service host
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Service host
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @name.setter
    def name(self, value):
        self._name = value or None

    @property
    def enabled(self):
        return self._enabled
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value)

    @property
    def version(self):
        return self._version
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @version.setter
    def version(self, value):
        self._version = value

    @property
    def port(self):
        return self._port
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @port.setter
    def port(self, value):
        self._port = value
