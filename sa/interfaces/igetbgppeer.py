# ---------------------------------------------------------------------
# IGetBGPPeer
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictListParameter,
    IPParameter,
    InterfaceNameParameter,
    StringParameter,
    IntParameter,
    BooleanParameter,
)


class IGetBGPPeer(BaseInterface):
    returns = DictListParameter(
        attrs={
            # Name of the forwarding instance
            "virtual_router": StringParameter(required=False),
            "peers": DictListParameter(
                attrs={
                    "type": StringParameter(choices=["internal", "external"], required=True),
                    "remote_address": IPParameter(),
                    "local_address": IPParameter(required=False),
                    "local_interface": InterfaceNameParameter(required=False),
                    "local_as": IntParameter(),
                    "remote_as": IntParameter(required=False),
                    "disabled": BooleanParameter(default=False),
                    "import_filter": StringParameter(required=False),
                    "export_filter": StringParameter(required=False),
                    # Detection time, microseconds
                    "timeout": IntParameter(),
                }
            ),
        }
    )
