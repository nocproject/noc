# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IGetDot11Associations(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "mac" : MACAddressParameter(),
        "ip"  : IPParameter(required=False),
    }))
