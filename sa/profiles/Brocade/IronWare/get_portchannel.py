# ---------------------------------------------------------------------
# Brocade.IronWare.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Brocade.IronWare.get_portchannel"
    interface = IGetPortchannel

    rx_trunk = re.compile(
        r"Trunk\sID\:\s(\d+)\nType:\s(\S+)\n.*\n.*\n.*\nPorts((\s+\d\/\d)+)", re.MULTILINE
    )

    def execute_cli(self):
        r = []
        # Get trunks
        st = self.cli("show trunk")
        for trunk in self.rx_trunk.findall(st):
            r += [{"interface": trunk[0], "members": trunk[2].split(), "type": trunk[1]}]
        return r
