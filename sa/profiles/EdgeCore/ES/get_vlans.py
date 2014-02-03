# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "EdgeCore.ES.get_vlans"
    cache = True
    implements = [IGetVlans]

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            # Try SNMP first
            try:
                oids = {}
                # Get VLAN names
                result = []
                for oid, v in self.snmp.getnext(
                        "1.3.6.1.2.1.17.7.1.4.3.1.1",
                        bulk=True):  # dot1qVlanStaticName
                    o = oid.split(".")[-1]
                    result += [{
                        "vlan_id":int(o),
                        "name":v.strip().rstrip('\x00')
                    }]
                return sorted(result, lambda x, y: cmp(x["vlan_id"],
                              y["vlan_id"]))
            except self.snmp.TimeOutError:
                # SNMP failed, continue with CLI
                pass
        ##
        ## ES4626 = Cisco Style
        ##
        if self.match_version(platform__contains="4626"):
            rx_vlan_line_4626 = re.compile(
                r"^\s*(?P<vlan_id>\d{1,4})"
                r"\s+(?P<name>\S+)\s+",
                re.IGNORECASE | re.MULTILINE)

            r = []
            vlans = self.cli("show vlan")
            for match in rx_vlan_line_4626.finditer(vlans):
                r += [{"vlan_id": int(match.group("vlan_id")),
                       "name": match.group("name")}]
            return r
        ##
        ## ES4612 or 3526S
        ##
        elif (self.match_version(platform__contains="4612") or
              self.match_version(platform__contains="3526S")):
            rx_vlan_line_4612 = re.compile(
                r"^\s*(?P<vlan_id>\d{1,4})"
                r"\s+\S+\s+(?P<name>\S+)\s+",
                re.IGNORECASE | re.MULTILINE)

            r = []
            vlans = self.cli("show vlan")
            for match in rx_vlan_line_4612.finditer(vlans):
                r += [{"vlan_id": int(match.group("vlan_id")),
                       "name": match.group("name")}]
            return r

        ##
        ## Other
        ##
        else:
            rx_vlan_line_3526 = re.compile(
                r"^VLAN ID\s*?:\s+?(?P<vlan_id>\d{1,4})\n"
                r".*?Name\s*?:\s+(?P<name>\S*?)\n",
                re.IGNORECASE | re.DOTALL | re.MULTILINE)

            r = []
            vlans = self.cli("show vlan")
            for match in rx_vlan_line_3526.finditer(vlans):
                r += [{"vlan_id": int(match.group("vlan_id")),
                       "name": match.group("name")}]
            return r
