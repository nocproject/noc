# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, ListOfParameter, DictParameter, MACAddressParameter, IPv4Parameter


class IGetDot11Associations(Interface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "mac": MACAddressParameter(),
        "ip": IPv4Parameter(required=False)
    }))
