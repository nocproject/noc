# ----------------------------------------------------------------------
# IGetInterfaceProperties interface
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    BooleanParameter,
    InterfaceNameParameter,
    IntParameter,
    DictListParameter,
    MACAddressParameter,
)


class IGetInterfaceProperties(BaseInterface):
    interface = InterfaceNameParameter(required=False)
    enable_ifindex = BooleanParameter(default=False)
    enable_interface_mac = BooleanParameter(default=False)
    enable_admin_status = BooleanParameter(default=False)
    enable_oper_status = BooleanParameter(default=False)
    returns = DictListParameter(
        attrs={
            "interface": InterfaceNameParameter(),
            "ifindex": IntParameter(required=False),
            "admin_status": BooleanParameter(required=False),
            "oper_status": BooleanParameter(required=False),
            "mac": MACAddressParameter(required=False),
        }
    )
