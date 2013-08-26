# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetChassisID
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from base import Interface, DictListParameter, MACAddressParameter


class IGetChassisID(Interface):
    returns = DictListParameter(attrs={
        "first_chassis_mac": MACAddressParameter(required=False),
        "last_chassis_mac": MACAddressParameter(required=False)
    }, convert=True)
    template = "interfaces/igetchassisid.html"
