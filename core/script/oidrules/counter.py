# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CounterRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .oid import OIDRule


class CounterRule(OIDRule):
    """
    SNMP OID for SNMP counters
    """
    name = "counter"
    default_type = "counter"
