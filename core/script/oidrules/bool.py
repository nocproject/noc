# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BooleanRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .oid import OIDRule


class BooleanRule(OIDRule):
    """
    SNMP OID for booleans
    """
    name = "bool"
    default_type = "bool"
