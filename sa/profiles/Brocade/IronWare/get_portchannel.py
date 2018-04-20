# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.IronWare.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Brocade.IronWare.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Brocade.IronWare.get_portchannel
    """
    name = "Brocade.IronWare.get_portchannel"
<<<<<<< HEAD
    interface = IGetPortchannel
=======
    implements = [IGetPortchannel]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_trunk = re.compile(
        r"Trunk\sID\:\s(\d+)\nType:\s(\S+)\n.*\n.*\n.*\nPorts((\s+\d\/\d)+)",
        re.MULTILINE)

    def execute(self):
        r = []
        # Get trunks
        st = self.cli("show trunk")
        for trunk in self.rx_trunk.findall(st):
            r += [{
                "interface": trunk[0],
                "members": trunk[2].split(),
                "type": trunk[1]
            }]
        return r
