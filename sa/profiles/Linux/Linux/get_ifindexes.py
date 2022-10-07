# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.Linux.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes


class Script(BaseScript):
    name = "Linux.Linux.get_ifindexes"
    interface = IGetIfindexes

    INTERFACE_NAME_OID = "IF-MIB::ifName"
