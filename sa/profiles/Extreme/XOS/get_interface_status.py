# ---------------------------------------------------------------------
# Extreme.XOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Extreme.XOS.get_interface_status"
    interface = IGetInterfaceStatus
    cache = True

    rx_snmp_name_eth = re.compile(
        r"^X\S+\s+Port\s+(?P<port>\d+(\:\d+)?)", re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    rx_port = re.compile(r"^\s*(?P<port>\d+(\:\d+)?)(?P<descr>.*)\n", re.MULTILINE)
    rx_port_status = re.compile(r"^\s*(?P<port>\S+)\s+[ED]\S+\s+(?P<state>\S+)", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        if self.has_snmp():
            try:
                # Get interface status
                # IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAlias, IF-MIB::ifPhysAddress
                for i, n, s, d, m in self.join_four_tables(
                    self.snmp,
                    "1.3.6.1.2.1.2.2.1.2",
                    "1.3.6.1.2.1.2.2.1.8",
                    "1.3.6.1.2.1.31.1.1.1.18",
                    "1.3.6.1.2.1.2.2.1.6",
                ):
                    match = self.rx_snmp_name_eth.search(n)
                    if i >= 1000000:
                        continue
                    if match:
                        n = match.group("port")
                        # print " !!! PORT --   %s " % n
                    macaddr = ""
                    if m:
                        macaddr = MACAddressParameter().clean(m)
                    r += [
                        {
                            "snmp_ifindex": i,
                            "interface": n,
                            "status": int(s) == 1,
                            "description": d,
                            "mac": macaddr,
                        }
                    ]  # ifOperStatus up(1)
                return r
            except self.snmp.TimeOutError:
                pass
        else:
            # Fallback to CLI
            v = self.cli("show ports description")
            for match in self.rx_port.finditer(v):
                port = match.group("port")
                c = self.cli("show ports %s information\n\x1b" % port)
                match1 = self.rx_port_status.search(c)
                r += [
                    {
                        "interface": port,
                        "status": match1.group("state") == "active",
                        "description": match.group("descr").strip(),
                    }
                ]
            return r

    # Generator returning a rows of 4 snmp tables joined by index
    def join_four_tables(
        self,
        snmp,
        oid1,
        oid2,
        oid3,
        oid4,
        community_suffix=None,
        min_index=None,
        max_index=None,
        cached=False,
    ):
        t1 = snmp.get_table(
            oid1,
            community_suffix=community_suffix,
            min_index=min_index,
            max_index=max_index,
            cached=cached,
        )
        t2 = snmp.get_table(
            oid2,
            community_suffix=community_suffix,
            min_index=min_index,
            max_index=max_index,
            cached=cached,
        )
        t3 = snmp.get_table(
            oid3,
            community_suffix=community_suffix,
            min_index=min_index,
            max_index=max_index,
            cached=cached,
        )
        t4 = snmp.get_table(
            oid4,
            community_suffix=community_suffix,
            min_index=min_index,
            max_index=max_index,
            cached=cached,
        )
        for k1, v1 in t1.items():
            try:
                yield k1, v1, t2[k1], t3[k1], t4[k1]
            except KeyError:
                pass
