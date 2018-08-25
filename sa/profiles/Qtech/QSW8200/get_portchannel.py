# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Qtech.QSW8200.get_portchannel"
    interface = IGetPortchannel
    cache = True

    rx_item = re.compile(
        r"^Group (?P<portgroup>\d+) information:\s*\n"
        r"^Mode\s*:\s*(?P<mode>\S+).+\n"
        r"^MinLinks\s*:.+\n"
        r"^UpLinks\s* :.+\n"
        r"^Member Port:(?P<members>.+)\n",
        re.MULTILINE
    )

    def execute(self):
        r = []
        cmd = self.cli("show port-channel", cached=True)
        for match in self.rx_item.finditer(cmd):
            members = match.group("members").split()
            r += [{
                "interface": "port-channel%s" % match.group("portgroup"),
                "members": members,
                "type": "L" if match.group("mode") == "Lacp" else "S"
            }]
        return r
