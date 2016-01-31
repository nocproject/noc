# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Huawei.VRP.get_portchannel"
    interface = IGetPortchannel

    def execute(self):
        r = self.cli("display link-aggregation summary")
        self.logger.error("Not implemented properly yet")
        return []
