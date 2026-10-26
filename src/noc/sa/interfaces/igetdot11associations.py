# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import DictParameter, IPv4Parameter, ListOfParameter, MACAddressParameter


class IGetDot11Associations(BaseInterface):
    returns = ListOfParameter(
        element=DictParameter(
            attrs={"mac": MACAddressParameter(), "ip": IPv4Parameter(required=False)}
        )
    )
