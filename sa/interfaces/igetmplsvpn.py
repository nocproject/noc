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
                   StringParameter, BooleanParameter, RDParameter, NoneParameter)
from noc.core.vpn import get_vpn_id


class IGetMPLSVPN(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        # VPN type
        "type": StringParameter(choices=["VRF", "VPLS", "VLL", "EVPN"]),
        # VPN state. True - active, False - inactive
        "status": BooleanParameter(default=True),
        # Box-unique VPN name
        "name": StringParameter(),
        # Optional description
        "description": StringParameter(required=False),
        # RFC2685 Global VPN ID
        # Autogenerated, if empty
        "vpn_id": StringParameter(required=False),
        # RD, may be omitted for VRF-lite
        "rd": NoneParameter() | RDParameter(),
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

    def clean_result(self, result):
        """
        Inject vpn_id
        :param result:
        :return:
        """
        result = super(IGetMPLSVPN, self).clean_result(result)
        for vpn in result:
            vpn["vpn_id"] = get_vpn_id(vpn)
        return result

    def script_clean_result(self, __profile, result):
        """
        Inject vpn_id
        :param result:
        :return:
        """
        result = super(IGetMPLSVPN, self).script_clean_result(__profile, result)
        for vpn in result:
            vpn["vpn_id"] = get_vpn_id(vpn)
        return result
