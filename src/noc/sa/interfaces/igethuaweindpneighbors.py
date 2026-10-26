# ---------------------------------------------------------------------
# IGetHuaweiNDPNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import DictListParameter, InterfaceNameParameter, MACAddressParameter, StringParameter


class IGetHuaweiNDPNeighbors(BaseInterface):
    """
    Huawei NDP neighbors interface
    """

    returns = DictListParameter(
        attrs={
            "local_interface": InterfaceNameParameter(),
            "neighbors": DictListParameter(
                attrs={
                    "chassis_mac": MACAddressParameter(),
                    "name": StringParameter(),
                    "interface": StringParameter(),
                }
            ),
        }
    )
