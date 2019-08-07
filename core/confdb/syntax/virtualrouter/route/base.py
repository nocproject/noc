# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB virtual router <name> route syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ...defs import DEF
from .inet.base import VR_ROUTE_INET_SYNTAX
from .inet6.base import VR_ROUTE_INET6_SYNTAX

VR_ROUTE_SYNTAX = DEF(
    "route",
    [
        VR_ROUTE_INET_SYNTAX,
        VR_ROUTE_INET6_SYNTAX,
    ],
)
