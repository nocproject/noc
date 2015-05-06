# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.CER-ADV.get_mpls_vpn
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMPLSVPN


class Script(NOCScript):
    name = 'Brocade.CER-ADV.get_mpls_vpn'
    implements = [IGetMPLSVPN]
    rx_line = re.compile('^(?P<vrf>.+?)\\s+(?P<rd>\\S+:\\S+|<not set>)\\s+[AI]\\s+\\|\\s+[AI]\\s*\\|\\s+[AI]\\s+(?P<iface>.*)$', re.IGNORECASE)

    def execute(self, **kwargs):
        vpns = []
        v = self.cli('show ip vrf')
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                iface = match.group('iface').strip()
                if iface:
                    interfaces = iface.split()
                else:
                    interfaces = []
                vpn = {'type': 'VRF',
                 'status': True,
                 'name': match.group('vrf'),
                 'interfaces': interfaces}
                rd = match.group('rd')
                if ':' in rd:
                    vpn['rd'] = rd
                vpns += [vpn]

        return vpns
