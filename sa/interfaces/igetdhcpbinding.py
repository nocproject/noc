# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetDHCPBinding interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface

from base import (ListOfParameter, DictParameter, IPv4Parameter,
                  MACAddressParameter, DateTimeParameter, StringParameter)


class IGetDHCPBinding(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "ip": IPv4Parameter(),
        "mac": MACAddressParameter(),
        "expiration": DateTimeParameter(),
        "type": StringParameter()  # Choices=["A","M"]
    }))
    preview = "NOC.sa.managedobject.scripts.ShowDHCPBinding"
