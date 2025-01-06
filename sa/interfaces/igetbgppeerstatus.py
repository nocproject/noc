# ---------------------------------------------------------------------
# IGetBGPPeerStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictListParameter, StringParameter, IntParameter, BooleanParameter, IPParameter


class IGetBGPPeerStatus(BaseInterface):
    """

    * neighbor - association identifier (IP Address)
    * admin_state - The desired state of the BGP connection:
        * start - True
        * stop - False
    * status - BGP peer connection state. one of:
        * idle(1)
        * connect(2)
        * active(3)
        * opensent(4)
        * openconfirm(5)
        * established(6)
    * table_version -
    """

    peers = DictListParameter(
        attrs={"peer": IPParameter(required=True)},
        required=False,
    )
    returns = DictListParameter(
        attrs={
            "neighbor": IPParameter(required=True),
            "admin_status": BooleanParameter(default=True),
            "status": StringParameter(
                choices=[
                    "active",
                    "connect",
                    "established",
                    "estabsync",
                    "idle",
                    "openconfirm",
                    "opensent",
                ],
                required=True,
            ),
            "table_version": IntParameter(required=False),
            "last_error": StringParameter(required=False),
        }
    )
