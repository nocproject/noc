# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface

from base import (ListOfParameter, DictParameter,
                  VLANIDParameter, StringParameter, StringListParameter)


class ISyncVlans(BaseInterface):
    vlans = ListOfParameter(element=DictParameter(attrs={
        "vlan_id": VLANIDParameter(),
        "name": StringParameter(required=False)
    }))
    tagged_ports = StringListParameter(default=[])
    returns = DictParameter(attrs={
        "created": ListOfParameter(element=VLANIDParameter()),
        "removed": ListOfParameter(element=VLANIDParameter())
    })
