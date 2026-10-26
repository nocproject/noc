# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import DictParameter, ListOfParameter, StringParameter, VLANIDParameter


class IGetVlans(BaseInterface):
    returns = ListOfParameter(
        element=DictParameter(
            attrs={"vlan_id": VLANIDParameter(), "name": StringParameter(required=False)}
        )
    )
    preview = "NOC.sa.managedobject.scripts.ShowVLANs"
