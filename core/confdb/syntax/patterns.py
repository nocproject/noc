# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB patterns
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Matches any token value
ANY = None
ANY = None
REST = True
VR_NAME = ANY
FI_NAME = ANY
IF_NAME = ANY
UNIT_NAME = ANY
IF_UNIT_NAME = ANY
IPv4_ADDRESS = ANY
IPv4_PREFIX = ANY
IPv6_ADDRESS = ANY
IPv6_PREFIX = ANY
IP_ADDRESS = ANY
ISO_ADDRESS = ANY
INTEGER = ANY
FLOAT = ANY
BOOL = ANY
ETHER_MODE = ANY
STP_MODE = ANY
HHMM = ANY


def CHOICES(*args):
    return ANY
