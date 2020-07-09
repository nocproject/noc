# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TPLink.T2600G.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "TPLink.T2600G.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
