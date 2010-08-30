# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetPortchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

##
## Port-channel information
##
class IGetPortchannel(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "interface" : InterfaceNameParameter(), # Port-channel name
        "members"   : ListOfParameter(element=InterfaceNameParameter()), # List of port-channel members
        "type"      : StringParameter(), # choices=["S","L"]. S - for static, L for LACP
    }))
