# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re

rx_ifc_status = re.compile(
    r"^\s*(?P<interface>[^ ]+) current state :.*?(?P<status>up|down)",
    re.IGNORECASE)
rx_ifc_block = re.compile(
    r"Interface\s+(PHY|Physical)\s+Protocol[^\n]+\n(?P<block>.*)$",
    re.MULTILINE | re.DOTALL | re.IGNORECASE)
rx_ifc_br_status = re.compile(
    r"^\s*(?P<interface>[^ ]+)\s+(?P<status>up|down|\*down).*$", re.IGNORECASE)


class Script(NOCScript):
    name = "Huawei.VRP.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r = []
                # IF-MIB::ifIndex, IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAlias
                for j, i, n, s, d in self.join_four_tables(self.snmp,
                    "1.3.6.1.2.1.2.2.1.1", "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", "1.3.6.1.2.1.31.1.1.1.18",
                    bulk=True):
                    r += [{"snmp_ifindex":i, "interface":n, "status":int(s) == 1, "description":d}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        ##
        ## VRP3 style
        ##
        if self.match_version(version__startswith="3."):
            for l in self.cli("display interface").splitlines():
                if (l.find(" current state :") != -1 \
                and l.find("Line protocol ") == -1):
                    match_int = rx_ifc_status.match(l)
                    if match_int:
                        r += [{
                            "interface": match_int.group("interface"),
                            "status": match_int.group("status").lower() == "up"
                        }]
        ##
        ## Other (VRP5 style)
        ##
        else:
            cli = self.cli("display interface brief", cached=True)
            match = rx_ifc_block.search(cli)
            if match:
                for l in match.group("block").splitlines():
                    match_int = rx_ifc_br_status.match(l)
                    if match_int:
                        r += [{
                            "interface": match_int.group("interface"),
                            "status": match_int.group("status").lower() == "up"
                        }]
        return r

    ##
    ## Generator returning a rows of 4 snmp tables joined by index, function copied from Edgecore.ES profile
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
