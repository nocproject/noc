# ---------------------------------------------------------------------
# Huawei.MA5600T.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Huawei.MA5600T.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    always_prefer = "S"

    rx_iface_sep = re.compile(r"^(\S+)\s+has\s+\d+\s+neighbors?", re.MULTILINE)

    # def execute_cli(self, **kwargs):
    #    v = self.cli("display lldp neighbor")
