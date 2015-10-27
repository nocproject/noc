# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus, MACAddressParameter
##
## @todo: CLI Support
##


class Script(NOCScript):
    name = "Extreme.XOS.get_interface_status"
    implements = [IGetInterfaceStatus]
    cache = True

    rx_snmp_name_eth = re.compile(r"^X\S+\s+Port\s+(?P<port>\d+)", re.MULTILINE | re.IGNORECASE | re.DOTALL)


    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAlias, IF-MIB::ifPhysAddress
                for i, n, s, d, m in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.2.2.1.8",
                    "1.3.6.1.2.1.31.1.1.1.18", "1.3.6.1.2.1.2.2.1.6",
                    bulk=True):
                    match = self.rx_snmp_name_eth.search(n)
                    if (i >= 1000000):
                       continue
                    if match:
                        n = match.group("port")
                        #print " !!! PORT --   %s " % n
                    macaddr = ""
                    if m:
                        macaddr = MACAddressParameter().clean(m)
                    r += [{"snmp_ifindex": i, "interface": n,
                           "status": int(s) == 1, "description": d,
                           "mac": macaddr}]  # ifOperStatus up(1)
                return r
            except self.snmp.TimeOutError:
                pass
            # Fallback to CLI

        r = []
        return r

    ##
    ## Generator returning a rows of 4 snmp tables joined by index
    ##
    def join_four_tables(self, snmp, oid1, oid2, oid3, oid4,
        community_suffix=None, bulk=False, min_index=None, max_index=None,
        cached=False):
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
