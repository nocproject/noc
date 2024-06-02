# ---------------------------------------------------------------------
# IGetPortchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import ListOfParameter, DictParameter, InterfaceNameParameter, StringParameter


class IGetPortchannel(BaseInterface):
    """
    Get port-channel information
    """

    returns = ListOfParameter(
        element=DictParameter(
            attrs={
                "interface": InterfaceNameParameter(),  # Port-channel name
                # List of port-channel members
                "members": ListOfParameter(element=InterfaceNameParameter()),
                "type": StringParameter(),
                # choices=["S","L"]. S - for static, L for LACP
            }
        )
    )
    preview = "NOC.sa.managedobject.scripts.ShowPortChannel"
