# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# NTP server host
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## NTP server host
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from base import BaseFact


class NTPServer(BaseFact):
    ATTRS = ["ip"]
    ID = ["ip"]

    def __init__(self, ip=None):
        super(NTPServer, self).__init__()
        self.ip = ip

    def __unicode__(self):
        return "NTPServer %s" % self.ip

    @property
    def ip(self):
        return self._ip
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @ip.setter
    def ip(self, value):
        self._ip = value or None
