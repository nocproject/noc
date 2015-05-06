# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetVlans(Interface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "vlan_id": VLANIDParameter(),
        "name": StringParameter(required=False)
    }))
    preview = "NOC.sa.managedobject.scripts.ShowVLANs"
