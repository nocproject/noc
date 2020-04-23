# ---------------------------------------------------------------------
# Linksys.SPS2xx.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Linksys.SPS2xx.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
