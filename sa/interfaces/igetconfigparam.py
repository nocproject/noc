# ---------------------------------------------------------------------
# IGetConfigParam interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictListParameter, StringParameter


class IGetDHCPBinding(BaseInterface):
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
                "units": StringParameter(required=False),
            }
        )
