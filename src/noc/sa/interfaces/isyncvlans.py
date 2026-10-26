# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import (
    DictListParameter,
    DictParameter,
    ListOfParameter,
    StringListParameter,
    StringParameter,
    VLANIDParameter,
)


class ISyncVlans(BaseInterface):
    vlans = DictListParameter(
        attrs={"vlan_id": VLANIDParameter(), "name": StringParameter(required=False)}
    )
    tagged_ports = StringListParameter(default=[])
    returns = DictParameter(
        attrs={
            "created": ListOfParameter(element=VLANIDParameter()),
            "removed": ListOfParameter(element=VLANIDParameter()),
        }
    )
