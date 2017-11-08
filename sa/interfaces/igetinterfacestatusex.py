# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetInterfaceStatusEx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.core.interface.base import BaseInterface

from base import (ListOfParameter, DictParameter,
                  InterfaceNameParameter, BooleanParameter,
                  IntParameter)


class IGetInterfaceStatusEx(BaseInterface):
    """
    Returns extended interface status for all available interfaces
    including port channels and SVI
    """
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "admin_status": BooleanParameter(default=False),
        "oper_status": BooleanParameter(default=False),
        "full_duplex": BooleanParameter(default=True),
        "last_change": IntParameter(required=False),
        # Input speed, kbit/s
        "in_speed": IntParameter(required=False),
        # Output speed, kbit/s
        "out_speed": IntParameter(required=False),
        # Configured bandwidth, kbit/s
        "bandwidth": IntParameter(required=False)
    }))
    preview = "NOC.sa.managedobject.scripts.ShowInterfaceStatusEx"
