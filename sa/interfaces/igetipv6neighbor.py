# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetIPv6Neighbor - interface to query IPv6 neighbor cache
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, StringParameter, DictParameter,
                  InterfaceNameParameter, IPv6Parameter, MACAddressParameter)


class IGetIPv6Neighbor(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetIPv6Neighbor - interface to query IPv6 neighbor cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetIPv6Neighbor(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
