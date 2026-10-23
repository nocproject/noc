# ---------------------------------------------------------------------
# HP.OfficeConnect.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "HP.OfficeConnect.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
