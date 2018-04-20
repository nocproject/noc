# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetOAMStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter, InterfaceNameParameter,
                  MACAddressParameter, StringParameter)


class IGetOAMStatus(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetOAMStatus interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetOAMStatus(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "remote_mac": MACAddressParameter(),
        "caps": ListOfParameter(element=StringParameter(choices=[
            "L",  # Link monitor
            "R",  # Remote loopback
            "U",  # Unidirection
            "V"   # Variable Request
        ]))
    }))
