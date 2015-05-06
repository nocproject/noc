# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.CER-ADV.get_ipv6_neighbor
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIPv6Neighbor


class Script(NOCScript):
    name = 'Brocade.CER-ADV.get_ipv6_neighbor'
    implements = [IGetIPv6Neighbor]
    rx_line = re.compile('^(?P<index>\\d+)\\s+(?P<ip>[0-9a-fA-F:\\.]+)\\s+\\d+\\s+(?P<mac>[0-9a-f]{4}\\.[0-9a-f]{4}\\.[0-9a-f]{4})\\s+(?P<state>\\S+)\\s+(?P<age>\\d+)\\s+(?P<interface>\\S+).*$')
    s_map = {'INCOMP': 'incomplete',
     'REACH': 'reachable',
     'STALE': 'stale',
     'DELAY': 'delay',
     'PROBE': 'probe'}

    def execute(self, vrf = None):
        cmd = 'show ipv6 neighbor'
        r = self.cli(cmd, list_re=self.rx_line)
        for n in r:
            n['state'] = self.s_map[n['state']]

        return r
