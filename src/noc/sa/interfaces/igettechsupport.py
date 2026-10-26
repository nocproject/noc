# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import DictParameter, ListOfParameter, StringParameter


class IGetTechSupport(BaseInterface):
    returns = (
        ListOfParameter(
            element=DictParameter(attrs={"name": StringParameter(), "section": StringParameter()})
        )
        | StringParameter()
    )
    preview = "NOC.sa.managedobject.scripts.TextPreview"
