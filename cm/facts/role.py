# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Performed role
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
class Role(BaseFact):
    ATTRS = ["name"]
    ID = ["name"]

    def __init__(self, name):
        super(Role, self).__init__()
        self.name = name

    def __str__(self):
        return self.name
