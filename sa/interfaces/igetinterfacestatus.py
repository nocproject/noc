# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetInterfaceStatus
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  InterfaceNameParameter, BooleanParameter)


#
# Returns a list of interfaces status (up/down),
# including port-channels and SVIs
#
class IGetInterfaceStatus(BaseInterface):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "status": BooleanParameter()
    }))
    preview = "NOC.sa.managedobject.scripts.ShowInterfaceStatus"
