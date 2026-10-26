# ---------------------------------------------------------------------
# IGetObjectStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import BooleanParameter, DictParameter, ListOfParameter, StringParameter


class IGetObjectStatus(BaseInterface):
    returns = ListOfParameter(
        element=DictParameter(attrs={"name": StringParameter(), "status": BooleanParameter()})
    )
    preview = "NOC.sa.managedobject.scripts.ShowObjectStatus"
