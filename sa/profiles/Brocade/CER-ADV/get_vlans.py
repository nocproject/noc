# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.CER-ADV.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    """
    Brocade.CER-ADV.get_vlans
    """
    name = 'Brocade.CER-ADV.get_vlans'
    implements = [IGetVlans]
    rx_vlan_line = re.compile('^\\S+\\s(?P<vlan_id>\\d+)\\,\\sName\\s(?P<name>[A-z0-9\\-\\_]+?),.+$')

    def execute(self):
        vlans = self.cli('show vlan')
        r = []
        for l in vlans.splitlines():
            match = self.rx_vlan_line.match(l.strip())
            if match:
                name = match.group('name')
                if name == '[None]':
                    name = ''
                vlan_id = int(match.group('vlan_id'))
                r += [{'vlan_id': vlan_id,
                  'name': name}]

        return r
