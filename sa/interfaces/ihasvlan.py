# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import VLANIDParameter, BooleanParameter


class IHasVlan(BaseInterface):
    vlan_id = VLANIDParameter()
    returns = BooleanParameter()
