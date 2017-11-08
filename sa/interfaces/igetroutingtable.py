# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IGetRoutingTable interface
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.core.interface.base import BaseInterface

from .base import (DictListParameter, StringParameter, RDParameter,
                   PrefixParameter, IntParameter, ListOfParameter,
                   IPParameter, InterfaceNameParameter, BooleanParameter)


class IGetRoutingTable(BaseInterface):
    returns = DictListParameter(attrs={
        # Name of the forwarding instance
        "forwarding_instance": StringParameter(default="default"),
        "virtual_router": StringParameter(required=False),
        "type": StringParameter(choices=["VRF", "VPLS", "VLL"], default="VRF"),
        "rd": RDParameter(required=False),
        "prefixes": DictListParameter(attrs={
            "prefix": PrefixParameter(required=True),
            # Address family
            "afi": StringParameter(choices=["IPv4", "IPv6"], required=False),
            # Tag
            "tag": IntParameter(required=False),
            "route": DictListParameter(attrs={
                # IP address next hop
                "next_hop": ListOfParameter(IPParameter(), required=False),
                # Interface via route
                "interface": InterfaceNameParameter(required=False),
                # Protocol learned route
                "protocol": StringParameter(choices=[
                    "LOCAL", "STATIC", "DIRECT", "CONNECTED", "AGGREGATE",
                    "RIP", "EIGRP", "OSPFv2", "OSPFv3",
                    "BGP", "ISIS", "LDP", "RSVP", "MPLS", "MVPN",
                    "PIM", "VPLS", "DVMRP", "KERNEL", "TUNNEL"
                ], required=True),
                # State of route
                "state": ListOfParameter(StringParameter(choices=[
                    "local", "internal", "external", "active"
                ]), required=False),
                # Selected route
                "selected": BooleanParameter(default=True),
                # Route metric
                "metric": IntParameter(required=False, default=1, min_value=0),
                # Local preference
                "local_pref": IntParameter(min_value=0, max_value=4294967295, required=False),
                "tag": IntParameter(required=False),
                # MPLS Label list
                "mpls_labels": ListOfParameter(IntParameter(), required=False),
                "as_path": ListOfParameter(IntParameter(min_value=0, max_value=4294967295), required=False)
            })
        })
    })
