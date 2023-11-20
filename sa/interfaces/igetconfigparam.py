# ---------------------------------------------------------------------
# IGetConfigParam interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictListParameter, StringParameter


class IGetConfigParam(BaseInterface):
    returns = DictListParameter(
        attrs={
            "param": StringParameter(required=True),
            "value": StringParameter(),
            "scopes": DictListParameter(
                attrs={
                    "scope": StringParameter(required=True),
                    "value": StringParameter(required=False),
                }
            ),
            "measurement": StringParameter(required=False),
        }
    )
