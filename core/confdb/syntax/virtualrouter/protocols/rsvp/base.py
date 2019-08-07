# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols rsvp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ....defs import DEF
from ....patterns import UNIT_NAME

RSVP_SYNTAX = DEF("rsvp", [DEF("interface", [DEF(UNIT_NAME, required=True, multi=True)])])
