# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetHuaweiNDPNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import (Interface, DictListParameter, StringParameter,
                  InterfaceNameParameter, MACAddressParameter)


class IGetHuaweiNDPNeighbors(Interface):
    """
    Huawei NDP neighbors interface
    """
    returns = DictListParameter(attrs={
        "local_interface": InterfaceNameParameter(),
        "neighbors": DictListParameter(attrs={
            "chassis_mac": MACAddressParameter(),
            "name": StringParameter(),
            "interface": StringParameter()
        })
    })
