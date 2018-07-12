# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes


class Script(BaseScript):
    name = "DLink.DVG.get_ifindexes"
    interface = IGetIfindexes
    requires = []
