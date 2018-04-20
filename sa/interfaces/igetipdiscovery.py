# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetIPDiscovery - interface to query ip discovery info
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter, InterfaceNameParameter,
                  RDParameter, StringParameter, IPParameter, MACAddressParameter)


class IGetIPDiscovery(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetIPDiscovery - interface to query ip discovery info
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetIPDiscovery(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "rd": RDParameter(required=False),
        "addresses": ListOfParameter(element=DictParameter(attrs={
            "ip": IPParameter(),
            "afi": StringParameter(choices=["4", "6"]),
            "mac": MACAddressParameter(required=False),
            "interface": InterfaceNameParameter(required=False)
        }))
    }))
