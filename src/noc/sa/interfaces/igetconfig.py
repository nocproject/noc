# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictParameter, ListOfParameter, StringParameter


class IGetConfig(BaseInterface):
    policy = StringParameter(
        choices=["r", "s"],  # Prefer running config  # Prefer startup config
        default="r",
        required=True,
    )
    returns = (
        ListOfParameter(
            element=DictParameter(attrs={"name": StringParameter(), "config": StringParameter()})
        )
        | StringParameter()
    )
    preview = "NOC.sa.managedobject.scripts.TextPreview"
