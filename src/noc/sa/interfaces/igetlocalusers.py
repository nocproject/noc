# ---------------------------------------------------------------------
# IGetUsers interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import BooleanParameter, DictParameter, ListOfParameter, StringParameter


#
# Commonly accepted classes are:
# superuser, operator
#
#
class IGetLocalUsers(BaseInterface):
    returns = ListOfParameter(
        element=DictParameter(
            attrs={
                "username": StringParameter(),
                "class": StringParameter(),
                "is_active": BooleanParameter(default=True),
            }
        )
    )
    preview = "NOC.sa.managedobject.scripts.ShowLocalUsers"
