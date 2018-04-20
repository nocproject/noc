# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "ip": IPv4Parameter(),
        "mac": MACAddressParameter(),
        "expiration": DateTimeParameter(),
        "type": StringParameter()  # Choices=["A","M"]
    }))
    preview = "NOC.sa.managedobject.scripts.ShowDHCPBinding"
