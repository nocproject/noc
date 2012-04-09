# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetInterfaceStatus
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


##
## Returns a list of interfaces status (up/down),
## including port-channels and SVIs
##
class IGetInterfaceStatus(Interface):
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "status": BooleanParameter()
    }))
    template = "interfaces/igetinterfacestatus.html"
