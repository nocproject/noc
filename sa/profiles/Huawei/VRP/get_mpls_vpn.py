# ---------------------------------------------------------------------
# Huawei.VRP.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mpls_vpn import Script as BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Huawei.VRP.get_mpls_vpn"
    interface = IGetMPLSVPN

    rx_line = re.compile(r"^\s+VPN\-Instance Name and ID :\s+(?P<vrf>\S+?),", re.IGNORECASE)
    rx_rd = re.compile(r"^\s+Route Distinguisher :\s+(?P<rd>\S+:\S+|<not set>)\s*", re.IGNORECASE)
    rx_int = re.compile(r"^(?:\s{,4}Interfaces :\s+|\s{6,})(?P<iface>.+?),?\s*$", re.IGNORECASE)
    rx_desc = re.compile(r"^\s+Description :\s+(?P<desc>.*)\s*", re.IGNORECASE)
    rx_import = re.compile(
        r"^\s+Import VPN Targets :\s+(?P<rt_import>(\S+:\S+\s*){1,}|<not set>)\s*", re.IGNORECASE
    )
    rx_export = re.compile(
        r"^\s+Export VPN Targets :\s+(?P<rt_export>(\S+:\S+\s*){1,}|<not set>)\s*", re.IGNORECASE
    )
    rx_rt_format = re.compile(r"(\d+\:\d+,?)+")
    rx_iface_format = re.compile(r"(\S+,?)+")
    rx_vpn = re.compile(
        r"^VPN\-Instance :\s+(?P<vrf>\S+)\s*\n"
        r"^\s+(?P<description>.*)\n"
        r"^\s+Route-Distinguisher :\s*\n"
        r"^\s+(?P<rd>\S+:\S+|<not set>)\s*\n"
        r"^\s+Interfaces :\s*\n"
        r"^\s+(?P<ifaces>.+)\s*\n",
        re.MULTILINE,
    )
    rx_vsi_split = re.compile(r"^\s+\*\*\*", re.MULTILINE)
    rx_vsi_pw_split = re.compile(r"^\s+\*\*", re.MULTILINE)
    rx_l2vc_split = re.compile(r"^\s+\*", re.MULTILINE)
    rx_l2vc_iface = re.compile(
        r"Interface Name\s+:\s*(?P<iface_name>\S+)\n"
        r"\s+State\s+:\s*\S+\n"
        r"\s+Access Port\s+:\s*\S+\n"
        r"\s+Last Up Time\s+:\s*\S+\s\S+\n"
        r"\s+Total Up Time\s+:\s*.+\n",
        re.MULTILINE,
    )

    l2vc_map = {
        "client interface": "interface",
        "vc id": "vpn_id",
        "vc type": "vc_type",
        "destination": "destination",
        "link state": "state",
    }

    vsi_instance_map = {
        "vsi name": "name",
        "vsi id": "vpn_id",
        # "interface name": "interface",
        # "state": "state",
        "vsi state": "vsi_state",
    }

    def execute_snmp(self, **kwargs):
        if self.is_ne_platform:
            # NE Platform Set 3 Type for import
            self.VRF_TYPE_MAP = {"rt_export": {"2"}, "rt_import": {"1", "3"}}
        return super().execute_snmp(**kwargs)

    def get_mpls_vpn(self):
        r = []
        # VPLS
        try:
            v = self.cli("display vsi verbose")
        except self.CLISyntaxError:
            return []
        for block in self.rx_vsi_split.split(v)[1:]:
            block = self.rx_vsi_pw_split.split(block)
            if len(block) == 2:
                block, pw_info = block
            else:
                block = block[0]
            p = {}
            ifaces = []
            for iface in self.rx_l2vc_iface.finditer(block):
                ifaces += [self.profile.convert_interface_name(iface.group("iface_name"))]
            # vsi, pwsignal, iface = block.split("\n\n")
            # for b in block.split("\n\n"):
            p.update(parse_kv(self.vsi_instance_map, block))
            r += [
                {
                    "type": "VPLS",
                    "status": p.get("vsi_state") == "up",
                    "name": p["name"],
                    "vpn_id": p.get("vpn_id"),
                    "interfaces": ifaces,
                }
            ]
        # VPWS
        try:
            v = self.cli("display mpls l2vc brief")
        except self.CLISyntaxError:
            return []
        for block in self.rx_l2vc_split.split(v)[1:]:
            p = parse_kv(self.l2vc_map, block)
            r += [
                {
                    "type": "VLL",
                    "status": p.get("state") == "up",
                    "name": p.get("vpn_id"),
                    "vpn_id": p.get("vpn_id"),
                    "interfaces": [self.profile.convert_interface_name(p["interface"])],
                }
            ]
        return r

    def execute_cli(self, **kwargs):
        vpns = []
        if self.capabilities.get("Network | LDP"):
            vpns += self.get_mpls_vpn()
        try:
            v = self.cli("display ip vpn-instance verbose")
        except self.CLISyntaxError:
            return []
        block = None
        block_splitter = None
        line_format = None
        for line in v.splitlines():
            match = self.rx_line.search(line)
            if match:
                vpns += [
                    {
                        "type": "VRF",
                        "status": True,
                        "vpn_id": "",
                        "name": match.group("vrf").strip(),
                        "interfaces": [],
                    }
                ]
            elif vpns:
                if block and line.startswith("    ") and line_format.match(line):
                    vpns[-1][block] += line.strip(" ,\n").split(block_splitter)
                    continue
                block = None
                block_splitter = None
                line_format = None
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
                    line_format = self.rx_iface_format
                    continue
                match_desc = self.rx_desc.match(line)
                if match_desc:
                    vpns[-1]["description"] = match_desc.group("desc").strip()
                    continue
                match_export = self.rx_export.match(line)
                if match_export:
                    vpns[-1]["rt_export"] = match_export.group("rt_export").split()
                    block = "rt_export"
                    line_format = self.rx_rt_format
                match_import = self.rx_import.match(line)
                if match_import:
                    vpns[-1]["rt_import"] = match_import.group("rt_import").split()
                    block = "rt_import"
                    line_format = self.rx_rt_format
        if vpns:
            return vpns
        # Second attempt
        for match in self.rx_vpn.finditer(v):
            vpn = {
                "type": "VRF",
                "status": True,
                "name": match.group("vrf").strip(),
                "vpn_id": "",
                "interfaces": match.group("ifaces").strip().split(" "),
            }
            description = match.group("description").strip()
            if description != "No description":
                vpn["description"] = description
            vpns += [vpn]
        return vpns
