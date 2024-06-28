# ---------------------------------------------------------------------
# NAG.SNR_eNOS.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "NAG.SNR_eNOS.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports=None):
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
        raise NotImplementedError()
