# ---------------------------------------------------------------------
# IGetCPEStatus
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictListParameter,
    InterfaceNameParameter,
    MACAddressParameter,
    BooleanParameter,
    IntParameter,
    StringParameter,
)


class IGetCPEStatus(BaseInterface):
    """
    Returns CPE status
    """

    cpes = DictListParameter(
        attrs={"local_id": StringParameter(required=True), "ifindex": IntParameter()},
        required=False,
    )
    returns = DictListParameter(
        attrs={
            "interface": InterfaceNameParameter(required=False),
            # Identifier over interface
            "local_id": StringParameter(required=True),
            "global_id": MACAddressParameter(accept_bin=False) | StringParameter(),
            "oper_status": BooleanParameter(default=False),
        }
    )
