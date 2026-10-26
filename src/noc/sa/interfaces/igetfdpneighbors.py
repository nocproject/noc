# ---------------------------------------------------------------------
# IGetFDPNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import DictParameter, InterfaceNameParameter, ListOfParameter, StringParameter


class IGetFDPNeighbors(BaseInterface):
    returns = DictParameter(
        attrs={
            # Local device id: FQDN or serial number
            "device_id": StringParameter(),
            "neighbors": ListOfParameter(
                element=DictParameter(
                    attrs={
                        # Remote device id: FQDN or serial number
                        "device_id": StringParameter(),
                        # Local interface
                        "local_interface": InterfaceNameParameter(),
                        # Remote interface
                        "remote_interface": StringParameter(),
                    }
                )
            ),
        }
    )
