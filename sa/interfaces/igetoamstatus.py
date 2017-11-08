# -*- coding: utf-8 -*-
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
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "remote_mac": MACAddressParameter(),
        "caps": ListOfParameter(element=StringParameter(choices=[
            "L",  # Link monitor
            "R",  # Remote loopback
            "U",  # Unidirection
            "V"  # Variable Request
        ]))
    }))
