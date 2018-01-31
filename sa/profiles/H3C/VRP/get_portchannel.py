# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# H3C.VRP.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "H3C.VRP.get_portchannel"
    interface = IGetPortchannel

    def execute(self):
        r = self.cli("display link-aggregation summary")
        if "No link-aggregation" in r:
            return []
        raise self.NotSupportedError()
