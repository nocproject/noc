# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetDHCPBinding interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IGetDHCPBinding(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "ip"         : IPParameter(),
        "mac"        : MACAddressParameter(),
        "expiration" : DateTimeParameter(),
        "type"       : StringParameter(), # Choices=["A","M"]
        }))
