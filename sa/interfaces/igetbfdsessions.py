# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetBFDSessions
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import *


class IGetBFDSessions(Interface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "peer": IPParameter(),
        "state": BooleanParameter(),  # True for Up
        "interface": InterfaceNameParameter(),
        # Transmit interval, microseconds
        "tx_interval": IntParameter(),
        "multiplier": IntParameter(),
        # Detection time, microseconds
        "detect_time": IntParameter()
        }))
    
    template = "interfaces/igetbfdsessions.html"
