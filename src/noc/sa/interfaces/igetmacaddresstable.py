# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    InterfaceNameParameter,
    ListOfParameter,
    StringParameter,
    VLANIDParameter,
    MACAddressParameter,
    DictParameter,
)


class IGetMACAddressTable(BaseInterface):
    interface = InterfaceNameParameter(required=False)
    vlan = VLANIDParameter(required=False)
    mac = MACAddressParameter(required=False)
    returns = ListOfParameter(
        element=DictParameter(
            attrs={
                "vlan_id": VLANIDParameter(),
                "mac": MACAddressParameter(),
                "interfaces": ListOfParameter(element=InterfaceNameParameter()),
                "type": StringParameter(choices=["D", "S", "C"]),  # Dynamic  # Static  # CPU
            }
        )
    )
    preview = "NOC.sa.managedobject.scripts.ShowMAC"
