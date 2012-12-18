# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetChassisID
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetChassisID(Interface):
    returns = DictParameter(attrs={
        "first_chassis_mac": MACAddressParameter(required=False),
        "last_chassis_mac": MACAddressParameter(required=False)
    })
    template = "interfaces/igetchassisid.html"
