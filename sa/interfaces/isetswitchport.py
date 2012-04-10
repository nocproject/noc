# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ISetSwitchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from base import *


class ISetSwitchport(Interface):
    # Port configuration
    configs = ListOfParameter(element=DictParameter(attrs={
        # Interface name
        "interface": InterfaceNameParameter(),
        # Port admin status: True - up, False - down
        "status": BooleanParameter(default=False),
        # Port description
        "description": StringParameter(required=False),
        # Untagged VLAN id
        "untagged": VLANIDParameter(required=False),
        # Tagged VLANS
        "tagged": ListOfParameter(element=VLANIDParameter(), default=[]),
        # STP edge port
        "edge_port": BooleanParameter(default=True)
    }))
    # Raise error if interface is not switchport
    protect_switchport = BooleanParameter(default=True)
    # Raise error when changing existing port type (tagged <-> untagged)
    protect_type = BooleanParameter(default=True)
    # Do not actually apply changes, just return them in "log"
    debug = BooleanParameter(default=False)

    returns = DictParameter(attrs={
        # Operation status. True - success, False - failure
        "status": BooleanParameter(),
        # Optional message
        "message": StringParameter(required=False),
        # Optional command log
        "log": StringParameter(required=False)
    })
