# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetPortchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetPortchannel(Interface):
    """
    Get port-channel information
    """
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),  # Port-channel name
        # List of port-channel members
        "members": ListOfParameter(element=InterfaceNameParameter()),
        "type": StringParameter()
        # choices=["S","L"]. S - for static, L for LACP
    }))
