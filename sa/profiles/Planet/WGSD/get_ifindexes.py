# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planet.WGSD.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes


class Script(BaseScript):
    name = "Planet.WGSD.get_ifindexes"
    interface = IGetIfindexes
    cache = True
    requires = []

    MAX_GETNEXT_RETIRES = 0
    INTERFACE_NAME_OID = "IF-MIB::ifName"
