# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetInterfaceStatusEx
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from base import (Interface, ListOfParameter, DictParameter,
                  InterfaceNameParameter, BooleanParameter,
                  IntParameter)


class IGetInterfaceStatusEx(Interface):
    """
    Returns extended interface status for all available interfaces
    including port channels and SVI
    """
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "admin_status": BooleanParameter(),
        "oper_status": BooleanParameter(),
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
