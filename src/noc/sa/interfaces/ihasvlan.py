# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import BooleanParameter, VLANIDParameter


class IHasVlan(BaseInterface):
    vlan_id = VLANIDParameter()
    returns = BooleanParameter()
