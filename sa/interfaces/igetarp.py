# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetARP - interface to query ARP cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import (Interface, StringParameter, InterfaceNameParameter, ListOfParameter,
                  DictParameter, IPv4Parameter, MACAddressParameter)


class IGetARP(Interface):
    vrf = StringParameter(required=False)
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "ip": IPv4Parameter(),
        # NONE for incomplete entries
        "mac": MACAddressParameter(required=False),
        # NONE for incomplete entries
        "interface": InterfaceNameParameter(required=False),
    }))
    preview = "NOC.sa.managedobject.scripts.ShowARP"
