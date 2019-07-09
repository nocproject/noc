# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VLAN
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from __future__ import absolute_import

# Third-party modules
import six

# NOC modules
from .base import BaseFact


@six.python_2_unicode_compatible
class VLAN(BaseFact):
    ATTRS = ["id", "name"]
    ID = ["id"]

    def __init__(self, id, name=None):
        super(VLAN, self).__init__()
        self.id = id
        self.name = name

    def __str__(self):
        r = "VLAN %d" % self.id
        if self.name and self.name != str(self.id):
            r += " (%s)" % self.name
        return r

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value:
            value = int(value)
        self._id = value or None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value or None
