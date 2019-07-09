# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NTP server host
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six

# NOC modules
from .base import BaseFact


@six.python_2_unicode_compatible
class NTPServer(BaseFact):
    ATTRS = ["ip"]
    ID = ["ip"]

    def __init__(self, ip=None):
        super(NTPServer, self).__init__()
        self.ip = ip

    def __str__(self):
        return "NTPServer %s" % self.ip

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value or None
