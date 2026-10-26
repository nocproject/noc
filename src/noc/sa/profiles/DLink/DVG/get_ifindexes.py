# ---------------------------------------------------------------------
# DLink.DVG.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript


class Script(BaseScript):
    name = "DLink.DVG.get_ifindexes"
    interface = IGetIfindexes
    requires = []
