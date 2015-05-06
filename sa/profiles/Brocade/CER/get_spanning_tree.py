# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.CER.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSpanningTree
from noc.lib.text import parse_table

class Script(NOCScript):
    name = 'Brocade.CER.get_spanning_tree'
    implements = [IGetSpanningTree]

    def process_pvst(self, cli_stp, proto):
        sep = 'Global STP (IEEE 802.1D) Parameters:'
        dsep = '======================================================================'
        port_rx = re.compile('\\d+\\/\\d+')
        glob_stp_rx = re.compile('(?P<vlan_id>\\d+)\\s+(?P<root_id>[0-9a-f]+)\\s+(?P<root_cost>\\d+)\\s+(?P<root_port>[0-9a-z/]+)\\s+(?P<priority>[0-9a-f]+)\\s+(\\d+\\s+){6}\\s+(?P<bridge_address>[0-9a-f]+)', re.DOTALL | re.IGNORECASE | re.MULTILINE)
        dpi_rx = re.compile('Interface:\\s(?P<dpi>[0-9/]+)')
        r = {'mode': proto,
         'instances': []}
        detail = self.cli('show span detail')
        for E in cli_stp.split(sep)[1:]:
            match = glob_stp_rx.search(E)
            interfaces = []
            for line in E.splitlines():
                if port_rx.match(line):
                    i = line.split()
                    state = i[3].lower()
                    vlan = match.group('vlan_id')
                    interface = i[0]
                    pos = detail.find('VLAN %s' % vlan)
                    v = detail[pos:].split(dsep)[1]
                    p = v.find('Port %s' % interface)
                    if dpi_rx.search(v[p:]):
                        dpi = dpi_rx.search(v[p:]).group('dpi')
                    else:
                        dpi = 0
                    interfaces += [{'interface': interface,
                      'port_id': 0,
                      'state': state if not state == 'blocking' else 'discarding',
                      'priority': i[1],
                      'designated_bridge_id': i[7][4:],
                      'designated_bridge_priority': i[7][:4],
                      'designated_port_id': '%s.%s' % (i[1], dpi),
                      'point_to_point': 0,
                      'edge': 0,
                      'role': 'unknown'}]

            r['instances'] += [{'id': vlan,
              'vlans': vlan,
              'root_id': match.group('root_id')[4:],
              'root_priority': match.group('root_id')[:4],
              'bridge_id': match.group('bridge_address'),
              'bridge_priority': match.group('priority'),
              'interfaces': interfaces}]

        return r

    def execute(self):
        v = self.cli('show span')
        return self.process_pvst(v, proto='PVST+')
