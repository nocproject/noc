# -*- coding: utf-8 -*-
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
