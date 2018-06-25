# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.WLC.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Cisco.IOS.get_cdp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(BaseScript):
    name = "Cisco.WLC.get_cdp_neighbors"
    interface = IGetCDPNeighbors
