# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import ListOfParameter, DictParameter, MACAddressParameter, IPv4Parameter


class IGetDot11Associations(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "mac": MACAddressParameter(),
        "ip": IPv4Parameter(required=False)
    }))
