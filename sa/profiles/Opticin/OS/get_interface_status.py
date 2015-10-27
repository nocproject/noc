# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus, MACAddressParameter
##
## @todo: ["mac"] support by SNMP
##


class Script(NOCScript):
    name = "Opticin.OS.get_interface_status"
    implements = [IGetInterfaceStatus]
    cache = True

    rx_interface = re.compile(r"(?P<interface>Port(\s|)\d{1,2})\s+(?P<admstatus>enable|disable)\s+(?P<status>up|down)",
        re.IGNORECASE | re.DOTALL)
    rx_snmp_name_eth = re.compile(r"(?P<port>\d{1,2})",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                 # IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAdminStatus, IF-MIB::ifPhysAddress
                for i, n, s, d, m in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.2.2.1.8",
                    "1.3.6.1.2.1.2.2.1.7", "1.3.6.1.2.1.2.2.1.6",
                    bulk=True):
                    match = self.rx_snmp_name_eth.search(n)
                    if match:
                        n = "Port " + match.group("port")
                    if n.startswith("CpuPort"):
                        continue
                    r += [{"snmp_ifindex": i, "interface": n,
                           "status": int(s) == 1,
                           "mac": MACAddressParameter().clean(m)}]  # ifOperStatus up(1)
                return r
            except self.snmp.TimeOutError:
                pass
            # Fallback to CLI
        r = []
        s = []

        cmd = "sh port state"
        buf = self.cli(cmd).lstrip("\n\n")
        for l in buf.split("\n"):
            match = self.rx_interface.search(l)
            if match:
                descr = ""
                interface = match.group("interface")
                linestatus = match.group("status")
                r += [{
                    "interface": interface,
                    "status": linestatus.lower() == "up",
                    }]
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
