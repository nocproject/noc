# ---------------------------------------------------------------------
# IGetObjectStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import ListOfParameter, DictParameter, StringParameter, BooleanParameter


class IGetObjectStatus(BaseInterface):
    returns = ListOfParameter(
        element=DictParameter(attrs={"name": StringParameter(), "status": BooleanParameter()})
    )
    preview = "NOC.sa.managedobject.scripts.ShowObjectStatus"
