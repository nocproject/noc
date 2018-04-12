# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetARP - interface to query ARP cache
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    StringParameter, InterfaceNameParameter, ListOfParameter,
    DictParameter, IPv4Parameter, MACAddressParameter
)


class IGetARP(BaseInterface):
    vrf = StringParameter(required=False)
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "vrf": StringParameter(required=False),
        "ip": IPv4Parameter(),
        # NONE for incomplete entries
        "mac": MACAddressParameter(required=False),
        # NONE for incomplete entries
        "interface": InterfaceNameParameter(required=False),
    }))
    preview = "NOC.sa.managedobject.scripts.ShowARP"
