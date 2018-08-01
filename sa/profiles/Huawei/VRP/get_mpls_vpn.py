# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_mpls_vpn import Script as BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(BaseScript):
    name = "Huawei.VRP.get_mpls_vpn"
    interface = IGetMPLSVPN

    rx_line = re.compile(r"^\s+VPN\-Instance Name and ID :\s+(?P<vrf>\S+?),", re.IGNORECASE)
    rx_rd = re.compile(r"^\s+Route Distinguisher :\s+(?P<rd>\S+:\S+|<not set>)\s*", re.IGNORECASE)
    rx_int = re.compile(r"^(?:\s{,4}Interfaces :\s+|\s{6,})(?P<iface>.+?),?\s*$", re.IGNORECASE)
    rx_desc = re.compile(r"^\s+Description :\s+(?P<desc>.*)\s*", re.IGNORECASE)
    rx_import = re.compile(r"^\s+Import VPN Targets :\s+(?P<rt_import>(\S+:\S+\s*){1,}|<not set>)\s*", re.IGNORECASE)
    rx_export = re.compile(r"^\s+Export VPN Targets :\s+(?P<rt_export>(\S+:\S+\s*){1,}|<not set>)\s*", re.IGNORECASE)
    rx_vpn = re.compile(
        r"^VPN\-Instance :\s+(?P<vrf>\S+)\s*\n"
        r"^\s+(?P<description>.*)\n"
        r"^\s+Route-Distinguisher :\s*\n"
        r"^\s+(?P<rd>\S+:\S+|<not set>)\s*\n"
        r"^\s+Interfaces :\s*\n"
        r"^\s+(?P<ifaces>.+)\s*\n", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        if self.is_ne_platform:
            # NE Platform Set 3 Type for import
            self.VRF_TYPE_MAP = {"rt_export": {"2"},
                                 "rt_import": {"1", "3"}}
        return super(Script, self).execute_snmp(**kwargs)

    def execute_cli(self, **kwargs):
        try:
            v = self.cli("display ip vpn-instance verbose")
        except self.CLISyntaxError:
            return []
        vpns = []
        block = None
        block_splitter = None
        for line in v.splitlines():
            match = self.rx_line.search(line)
            if match:
                vpns += [{
                    "type": "VRF",
                    "status": True,
                    "vpn_id": "",
                    "name": match.group("vrf").strip(),
                    "interfaces": []
                }]
            elif vpns:
                if block and line.startswith("    "):
                    vpns[-1][block] += line.strip(" ,\n").split(block_splitter)
                    continue
                block = None
                block_splitter = None
                match_rd = self.rx_rd.match(line)
                if match_rd:
                    rd = match_rd.group("rd")
                    if ":" in rd:
                        vpns[-1]["rd"] = rd
                    continue
                match_int = self.rx_int.match(line)
                if match_int:
                    vpns[-1]["interfaces"] += [match_int.group("iface").strip("\n")]
                    block, block_splitter = "interfaces", ","
                    continue
                match_desc = self.rx_desc.match(line)
                if match_desc:
                    vpns[-1]["description"] = match_desc.group("desc").strip()
                    continue
                match_export = self.rx_export.match(line)
                if match_export:
                    vpns[-1]["rt_export"] = match_export.group("rt_export").split()
                    block = "rt_export"
                match_import = self.rx_import.match(line)
                if match_import:
                    vpns[-1]["rt_import"] = match_import.group("rt_import").split()
                    block = "rt_import"

        if vpns:
            return vpns
        # Second attempt
        for match in self.rx_vpn.finditer(v):
            vpn = {
                "type": "VRF",
                "status": True,
                "name": match.group("vrf").strip(),
                "vpn_id": "",
                "interfaces": match.group("ifaces").strip().split(" ")
            }
            description = match.group("description").strip()
            if description != "No description":
                vpn["description"] = description
            vpns += [vpn]
        return vpns
