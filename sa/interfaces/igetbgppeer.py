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
    BooleanParameter,
    ASNParameter,
    RDParameter,
)


class IGetBGPPeer(BaseInterface):
    returns = DictListParameter(
        attrs={
            # Name of the forwarding instance
            "virtual_router": StringParameter(required=False),
            "router_id": RDParameter(required=False),
            "peers": DictListParameter(
                attrs={
                    "type": StringParameter(choices=["internal", "external"], required=True),
                    "local_as": ASNParameter(),
                    "remote_address": IPParameter(),
                    "remote_as": ASNParameter(required=False),
                    "local_address": IPParameter(required=False),
                    "local_interface": InterfaceNameParameter(required=False),
                    "disabled": BooleanParameter(default=False),
                    "import_filter": StringParameter(required=False),
                    "export_filter": StringParameter(required=False),
                    # Detection time, microseconds
                }
            ),
        }
    )
