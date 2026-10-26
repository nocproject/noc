# ---------------------------------------------------------------------
# ZTE.ZXA10.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript


class Script(BaseScript):
    name = "ZTE.ZXA10.get_ifindexes"
    interface = IGetIfindexes

    INTERFACE_NAME_OID = "IF-MIB::ifName"
