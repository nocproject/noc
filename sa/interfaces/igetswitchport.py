# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetSwitchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter, DictListParameter, VLANIDParameter,
                  InterfaceNameParameter, StringParameter, BooleanParameter)


#
# All L2 switched interfaces on box
# Port-channel members must be returned as elements in "members" field,
# Not as separate entry
#
# For Q-in-Q tunneling both "802.1Q Enabled" and "802.1ad Tunnel"
# must be set to True, while "untagged" must contain top label
#
class IGetSwitchport(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        # Interface name
        "interface": InterfaceNameParameter(),
        # Operational status. True - Up, False - Down
        "status": BooleanParameter(default=False),
        # Optional interface description
        "description": StringParameter(required=False),
        # 802.1Q VLAN Tagging enabled
        "802.1Q Enabled": BooleanParameter(default=False),
        # Q-in-Q tunneling
        "802.1ad Tunnel": BooleanParameter(default=False),
        # Default, native, PVID
        "default_vlan": VLANIDParameter(required=False),
        # List of tagged vlans
        "tagged": ListOfParameter(element=VLANIDParameter()),
        # List of untagged VLAN
        "untagged": ListOfParameter(element=VLANIDParameter()),
        "type": StringParameter(choices=["hybrid", ]),
        "dynamic_vlans": DictListParameter(attrs={
            "vlan": VLANIDParameter(),
            "service": StringParameter(
                choices=[
                    "voice",
                    "mvr",
                    "multicast"
                ]
            )
        }),
        # List of port-channel members, if applicable
        "members": ListOfParameter(element=InterfaceNameParameter())
    }))
