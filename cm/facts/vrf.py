# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRF fact
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
class VRF(BaseFact):
    ATTRS = ["name", "rd"]
    ID = ["name", "rd"]

    def __init__(self, name, rd=None):
        super(VRF, self).__init__()
        self.name = name
        self.rd = rd

    def __str__(self):
        return "VRF %s" % self.name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value or None

    @property
    def rd(self):
        return self._rd

    @rd.setter
    def rd(self, value):
        self._rd = value or None
