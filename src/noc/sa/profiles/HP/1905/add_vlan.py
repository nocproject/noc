# ---------------------------------------------------------------------
# HP.1905.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "HP.1905.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports=None):
        raise NotImplementedError()
