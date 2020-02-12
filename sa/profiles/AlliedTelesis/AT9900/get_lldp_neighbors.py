# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT9900.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
