# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetMPLSVPN interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (ListOfParameter, DictParameter, InterfaceNameParameter,
                   StringParameter, BooleanParameter, RDParameter)


class IGetMPLSVPN(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        # VPN type
        "type": StringParameter(choices=["VRF", "VPLS", "VLL"]),
        # VPN state. True - active, False - inactive
        "status": BooleanParameter(default=True),
        # Box-unique VPN name
        "name": StringParameter(),
        # Optional description
        "description": StringParameter(required=False),
        # RD, may be omitted for VRF-lite
        "rd": RDParameter(required=False),
        # Route-target export for VRF
        "rt_export": ListOfParameter(
            element=RDParameter(),
            required=False
        ),
        # Route-target import for VRF
        "rt_import": ListOfParameter(
            element=RDParameter(),
            required=False
        ),
        # List of interfaces
        "interfaces": ListOfParameter(element=InterfaceNameParameter())
    }))
    preview = "NOC.sa.managedobject.scripts.ShowMPLSVPN"
