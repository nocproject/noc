# ---------------------------------------------------------------------
# IGetBFDSessions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import (
    DictListParameter,
    InterfaceNameParameter,
    IntParameter,
    IPParameter,
    ListOfParameter,
    StringParameter,
)


class IGetBFDSessions(BaseInterface):
    returns = DictListParameter(
        attrs={
            "local_address": IPParameter(required=False),
            "remote_address": IPParameter(),
            "local_interface": InterfaceNameParameter(),
            "local_discriminator": IntParameter(),
            "remote_discriminator": IntParameter(),
            "state": StringParameter(choices=["UP", "DOWN"]),
            "clients": ListOfParameter(
                element=StringParameter(
                    choices=["L2", "RSVP", "ISIS", "OSPF", "BGP", "EIGRP", "PIM", "IFNET", "BFD"]
                )
            ),
            # Transmit interval, microseconds
            "tx_interval": IntParameter(),
            "multiplier": IntParameter(),
            # Detection time, microseconds
            "detect_time": IntParameter(),
        }
    )
