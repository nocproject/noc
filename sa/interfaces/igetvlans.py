# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  StringParameter, VLANIDParameter)


class IGetVlans(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "vlan_id": VLANIDParameter(),
        "name": StringParameter(required=False)
    }))
    preview = "NOC.sa.managedobject.scripts.ShowVLANs"
