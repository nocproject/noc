# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_ipv6_neighbor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetipv6neighbor import IGetIPv6Neighbor


class Script(BaseScript):
    name = "Juniper.JUNOS.get_ipv6_neighbor"
    interface = IGetIPv6Neighbor

    rx_line = re.compile(
        r"^(?P<ip>[0-9a-f:]+)\s+"
        r"(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:"
        r"[0-9a-f]{2}:[0-9a-f]{2})\s+"
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_ipv6_neighbor
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIPv6Neighbor

class Script(NOCScript):
    name = "Juniper.JUNOS.get_ipv6_neighbor"
    implements = [IGetIPv6Neighbor]

    rx_line = re.compile(
        r"^(?P<ip>[0-9a-f:]+)\s+"
        r"(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r"(?P<state>\S+)\s+\S+\s+\S+\s+\S+\s+(?P<interface>\S+)\s*$")

    def execute(self, vrf=None):
        cmd = "show ipv6 neighbor"
        return self.cli(cmd, list_re=self.rx_line)
