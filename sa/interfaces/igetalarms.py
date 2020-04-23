# ---------------------------------------------------------------------
# IGetAlarms - interface to query alarm device table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from datetime import datetime

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    StringParameter,
    DateTimeParameter,
    StringListParameter,
    DictParameter,
    DictListParameter,
)


class IGetAlarms(BaseInterface):
    """
    * ts -
    * id - local device alarm id, if empty - generate by hash on timestamp and path and vendor_code
    * path - list component (chassis, interface, board) affected alarm. Example CPE - [<CPE_ID>]
    * vendor_code - local AlarmClass on device
    * message - Full alarm message
    * attributes - additional sctructured vars on alarm
    """

    returns = DictListParameter(
        attrs={
            # Time message created
            "ts": DateTimeParameter(default=datetime.now()),
            # Message id
            "id": StringParameter(),
            # Component path to generated message (ex. chassis, slot, interface)
            "path": StringListParameter(required=False),
            # Message category (ex facility or tag for syslog)
            "vendor_code": StringParameter(),
            # Message full text
            "message": StringParameter(),
            # Additional attributes
            "attributes": DictParameter(required=False),
        }
    )
