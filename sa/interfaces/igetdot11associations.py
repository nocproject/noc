# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import ListOfParameter, DictParameter, MACAddressParameter, IPv4Parameter


<<<<<<< HEAD
class IGetDot11Associations(BaseInterface):
=======
class IGetDot11Associations(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "mac": MACAddressParameter(),
        "ip": IPv4Parameter(required=False)
    }))
