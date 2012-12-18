# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetDiscoveryID
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import (DictParameter, Interface, MACAddressParameter,
                  StringParameter, IPParameter)


class IGetDiscoveryID(Interface):
    returns = DictParameter(attrs={
        # Chassis MAC interval
        "first_chassis_mac": MACAddressParameter(required=False),
        "last_chassis_mac": MACAddressParameter(required=False),
        # FQDN
        "hostname": StringParameter(required=False),
        # Router ID/Loopback address
        "router_id": IPParameter(required=False)
    })
