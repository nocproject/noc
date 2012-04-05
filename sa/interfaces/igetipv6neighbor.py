# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetIPv6Neighbor - interface to query IPv6 neighbor cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetIPv6Neighbor(Interface):
    vrf = StringParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "ip": IPv6Parameter(),
        # NONE for incomplete entries
        "mac": MACAddressParameter(required=False),
        # NONE for incomplete entries
        "interface": InterfaceNameParameter(required=False),
        # Neighbor state as defined be RFC 2461
        "state": StringParameter(choices=[
            "incomplete",
            "reachable",
            "stale",
            "delay",
            "probe"])
    }))
