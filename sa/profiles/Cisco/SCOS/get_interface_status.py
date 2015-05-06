# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SCOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus, MACAddressParameter

##
## Only SNMP implementation
##

class Script(NOCScript):
    name = "Cisco.SCOS.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for i, a, n, s, m in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.7", "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", "1.3.6.1.2.1.2.2.1.6", bulk=True):
                    # ifOperStatus up(1)
                    mac = MACAddressParameter().clean(m) if m else None
                    r += [{
                        "snmp_ifindex": i,
                        "interface": n,
                        "status": int(s) == 1,
                        "mac": mac
                    }]
                return r
            except self.snmp.TimeOutError:
                pass

    def join_four_tables(self, snmp, oid1, oid2, oid3, oid4,
        community_suffix=None, bulk=False, min_index=None, max_index=None,
        cached=False):
        """
        Generator returning a rows of 4 snmp tables joined by index
        """
        t1 = snmp.get_table(oid1, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        t2 = snmp.get_table(oid2, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        t3 = snmp.get_table(oid3, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        t4 = snmp.get_table(oid4, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        for k1, v1 in t1.items():
            try:
                yield (k1, v1, t2[k1], t3[k1], t4[k1])
            except KeyError:
                pass
