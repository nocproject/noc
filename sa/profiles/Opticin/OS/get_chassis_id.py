# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID, MACAddressParameter

class Script(BaseScript):
    name = "Opticin.OS.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac = re.compile(r"System MAC[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        if self.has_snmp():
            try:
                # Get interface physAddress
                # IF-MIB::ifPhysAddress
                for i, m in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.6",
                    bulk=True):
                    if i == 1:
                        first_mac = MACAddressParameter().clean(m)
                    last_mac = MACAddressParameter().clean(m)

                return {
                    "first_chassis_mac": first_mac,
                    "last_chassis_mac": last_mac
                }
                    
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
        mac = MACAddressParameter().clean(match.group("id"))
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }


    def join_four_tables(self, snmp, oid1,
        community_suffix=None, bulk=False, min_index=None, max_index=None,
        cached=False):       
        t1 = snmp.get_table(oid1, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        for k1, v1 in t1.items():
            try:
                yield (k1, v1)
            except KeyError:
                pass
