# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetARP - interface to query ARP cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IGetARP(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
            "ip"         : IPParameter(),
            "mac"        : MACAddressParameter(required=False), # NONE for incomplete entries
            "interface"  : StringParameter(required=False),     # NONE for incomplete entries
            }))
