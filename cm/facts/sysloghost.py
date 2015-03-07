# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syslog host
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class SyslogHost(BaseFact):
    ATTRS = ["ip"]

    def __init__(self, ip=None):
        super(SyslogHost, self).__init__()
        self.ip = ip

    def __unicode__(self):
        return "SyslogHost %s" % self.ip

    @property
    def ip(self):
        return self._ip
    
    @ip.setter
    def ip(self, value):
        self._ip = value or None
