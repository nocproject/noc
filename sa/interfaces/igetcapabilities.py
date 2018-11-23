# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetCapabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictParameter, StringListParameter


class IGetCapabilities(BaseInterface):
    only = StringListParameter(choices=[
        # SNMP sections
        "snmp", "snmp_v1", "snmp_v2c",
        # L2 sections
        "bfd", "cdp", "fdp", "huawei_ndp", "lacp", "lldp", "oam", "rep", "stp", "udld",
        # L3 sections
        "hsrp", "vrrp", "vrrpv3", "bgp", "ospf", "ospfv3", "isis", "ldp", "rsvp"
    ], required=False)
    returns = DictParameter()
