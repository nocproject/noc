# ---------------------------------------------------------------------
# IGetInterfaceStatus
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import ListOfParameter, DictParameter, InterfaceNameParameter, BooleanParameter


#
# Returns a list of interfaces status (up/down),
# including port-channels and SVIs
#
class IGetInterfaceStatus(BaseInterface):
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(
        element=DictParameter(
            attrs={"interface": InterfaceNameParameter(), "status": BooleanParameter()}
        )
    )
    preview = "NOC.sa.managedobject.scripts.ShowInterfaceStatus"
