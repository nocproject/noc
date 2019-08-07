# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB hints protocols syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ..defs import DEF
from .lldp.hints import HINTS_PROTOCOLS_LLDP
from .spanningtree.hints import HINTS_PROTOCOLS_SPANNING_TREE
from .loopdetect.hints import HINTS_PROTOCOLS_LOOP_DETECT

PROTOCOLS_HINTS_SYNTAX = DEF(
    "hints", [HINTS_PROTOCOLS_LLDP, HINTS_PROTOCOLS_SPANNING_TREE, HINTS_PROTOCOLS_LOOP_DETECT]
)
