# ---------------------------------------------------------------------
# Harmonic.ProStream1000.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from xml.dom.minidom import parseString

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Harmonic.ProStream1000.get_config"
    interface = IGetConfig

    DATA = '<AFRICA><Platform ID="1" Action="GET_TREE" /></AFRICA>'
    rx_sub = re.compile("\n\t+\n+", re.MULTILINE | re.DOTALL)

    def execute(self, **kwargs):
        config = self.http.get("/BrowseConfig", data=self.DATA, use_basic=True)
        config = self.strip_first_lines(config, 1)
        config = parseString(config)
        config = config.toprettyxml()
        config = self.rx_sub.sub("\n", config)
        config = config.replace(">\n</", "></")
        return config
