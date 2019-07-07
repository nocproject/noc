# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(BaseScript):
    name = "Juniper.JUNOS.get_mpls_vpn"
    interface = IGetMPLSVPN

    rx_ri = re.compile(
        r"(?P<name>\S+?):\n"
        r"(?:  Description: (?P<description>.+?)\n)?"
        r"  Router ID: \S+\n"
        r"  Type: (?P<type>\S+)\s+\S*\s+State:\s+(?P<status>Active|Inactive)\s*\n"
        r"  Interfaces:\n"
        r"(?P<ifaces>(?:    \S+\n)*)"
        r"(  Route-distinguisher: (?P<rd>\S+)\s*\n)?"
        r"(  Vrf-import: \[(?P<vrf_import>.+)\]\s*\n)?"
        r"(  Vrf-export: \[(?P<vrf_export>.+)\]\s*\n)?",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_vrf_target = re.compile(r"target:(?P<rd>\d+:\d+)")
    type_map = {"vrf": "VRF", "vpls": "VPLS", "l2vpn": "VLL", "evpn": "EVPN"}

    def execute(self, **kwargs):
        c = self.cli(
            'help apropos "instance" | match "^show route instance" ',
            cached=True,
            ignore_errors=True,
        )
        if "show route instance" not in c:
            return []

        vpns = []
        v = self.cli("show route instance detail")
        for match in self.rx_ri.finditer(v):
            name = match.group("name")
            rt = match.group("type").lower()
            if name == "master" or name.startswith("__") or rt not in self.type_map:
                continue
            interfaces = [x.strip() for x in match.group("ifaces").splitlines()]
            interfaces = [x for x in interfaces if x and not x.startswith("lsi.")]
            vpn = {
                "type": self.type_map[rt],
                "status": match.group("status").lower() == "active",
                "name": name,
                "rd": match.group("rd"),
                "interfaces": interfaces,
            }
            description = match.group("description")
            if description:
                vpn["description"] = description.strip()
            if match.group("vrf_import"):
                vpn["rt_import"] = []
                for rt_name in match.group("vrf_import").split(" "):
                    rt_name = rt_name.strip()
                    if rt_name == "":
                        continue
                    if rt_name.startswith("target:"):
                        vpn["rt_import"] += [rt_name[7:]]
                    c = self.cli("show policy %s" % rt_name)
                    for rd in self.rx_vrf_target.finditer(c):
                        vpn["rt_import"] += [rd.group("rd")]
            if match.group("vrf_export"):
                vpn["rt_export"] = []
                for rt_name in match.group("vrf_export").split(" "):
                    rt_name = rt_name.strip()
                    if rt_name == "":
                        continue
                    if rt_name.startswith("target:"):
                        vpn["rt_export"] += [rt_name[7:]]
                    c = self.cli("show policy %s" % rt_name)
                    for rd in self.rx_vrf_target.finditer(c):
                        vpn["rt_export"] += [rd.group("rd")]
            vpns += [vpn]
        return vpns
