# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Extreme.XOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.sa.interfaces.base import MACAddressParameter

#
# @todo: CLI Support
#


class Script(BaseScript):
    name = "Extreme.XOS.get_interface_status"
    interface = IGetInterfaceStatus
    cache = True

    rx_snmp_name_eth = re.compile(
        r"^X\S+\s+Port\s+(?P<port>\d+(\:\d+)?)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_port = re.compile(
        r"^\s*(?P<port>\d+(\:\d+)?)(?P<descr>.*)\n", re.MULTILINE)
    rx_port_status = re.compile(
        r"^\s*(?P<port>\S+)\s+[ED]\S+\s+(?P<state>\S+)", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        if self.has_snmp():
            try:
                # Get interface status
                # IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAlias, IF-MIB::ifPhysAddress
                for i, n, s, d, m in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.2.2.1.8",
                    "1.3.6.1.2.1.31.1.1.1.18", "1.3.6.1.2.1.2.2.1.6"
                ):
=======
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
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAlias, IF-MIB::ifPhysAddress
                for i, n, s, d, m in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.2.2.1.8",
                    "1.3.6.1.2.1.31.1.1.1.18", "1.3.6.1.2.1.2.2.1.6",
                    bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    match = self.rx_snmp_name_eth.search(n)
                    if (i >= 1000000):
                       continue
                    if match:
                        n = match.group("port")
<<<<<<< HEAD
                        # print " !!! PORT --   %s " % n
=======
                        #print " !!! PORT --   %s " % n
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    macaddr = ""
                    if m:
                        macaddr = MACAddressParameter().clean(m)
                    r += [{"snmp_ifindex": i, "interface": n,
                           "status": int(s) == 1, "description": d,
                           "mac": macaddr}]  # ifOperStatus up(1)
                return r
            except self.snmp.TimeOutError:
                pass
<<<<<<< HEAD
        else:
            # Fallback to CLI
            v = self.cli("show ports description")
            for match in self.rx_port.finditer(v):
                port = match.group("port")
                c = self.cli("show ports %s information\n\x1B" % port)
                match1 = self.rx_port_status.search(c)
                r += [{
                    "interface": port,
                    "status": match1.group("state") == "active",
                    "description": match.group("descr").strip()
                }]
            return r
=======
            # Fallback to CLI

        r = []
        return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    ##
    ## Generator returning a rows of 4 snmp tables joined by index
    ##
    def join_four_tables(self, snmp, oid1, oid2, oid3, oid4,
<<<<<<< HEAD
        community_suffix=None, min_index=None, max_index=None,
        cached=False):
        t1 = snmp.get_table(oid1, community_suffix=community_suffix,
            min_index=min_index, max_index=max_index, cached=cached)
        t2 = snmp.get_table(oid2, community_suffix=community_suffix,
            min_index=min_index, max_index=max_index, cached=cached)
        t3 = snmp.get_table(oid3, community_suffix=community_suffix,
            min_index=min_index, max_index=max_index, cached=cached)
        t4 = snmp.get_table(oid4, community_suffix=community_suffix,
=======
        community_suffix=None, bulk=False, min_index=None, max_index=None,
        cached=False):
        t1 = snmp.get_table(oid1, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        t2 = snmp.get_table(oid2, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        t3 = snmp.get_table(oid3, community_suffix=community_suffix, bulk=bulk,
            min_index=min_index, max_index=max_index, cached=cached)
        t4 = snmp.get_table(oid4, community_suffix=community_suffix, bulk=bulk,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            min_index=min_index, max_index=max_index, cached=cached)
        for k1, v1 in t1.items():
            try:
                yield (k1, v1, t2[k1], t3[k1], t4[k1])
            except KeyError:
                pass
