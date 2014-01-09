# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetMACAddressTable(Interface):
    interface = InterfaceNameParameter(required=False)
    vlan = VLANIDParameter(required=False)
    mac = MACAddressParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "vlan_id": VLANIDParameter(),
        "mac": MACAddressParameter(),
        "interfaces": ListOfParameter(element=InterfaceNameParameter()),
        "type": StringParameter()  # choices=["D","S"]
    }))
    preview = "NOC.sa.managedobject.scripts.ShowMAC"
