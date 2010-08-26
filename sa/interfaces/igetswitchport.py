# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetSwitchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *
##
## All L2 switched interfaces on box
## Port-channel members must be returned as elements in "members" field,
## Not as separate entry
##
## For Q-in-Q tunneling both "802.1Q Enabled" and "802.1ad Tunnel" must be set to True,
## while "untagged" must contain top label
##
class IGetSwitchport(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "interface"      : InterfaceNameParameter(),                          # Interface name
        "status"         : BooleanParameter(default=False),                   # Operational status. True - Up, False - Down
        "description"    : StringParameter(required=False),                   # Optional interface description
        "802.1Q Enabled" : BooleanParameter(default=False),                   # 802.1Q VLAN Tagging enabled
        "802.1ad Tunnel" : BooleanParameter(default=False),                   # Q-in-Q tunneling
        "untagged"       : VLANIDParameter(required=False),                   # Untagged VLAN if present
        "tagged"         : ListOfParameter(element=VLANIDParameter()),        # List of tagged vlans
        "members"        : ListOfParameter(element=InterfaceNameParameter()), # List of port-channel members, if applicable
    }))
