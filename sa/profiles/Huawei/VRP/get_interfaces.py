# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
from typing import (
    Dict,
    Union,
    DefaultDict,
)
import re
from collections import defaultdict
from itertools import compress, chain


# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.validators import is_vlan
from noc.core.mib import mib
from noc.core.snmp.render import render_bin
from noc.core.text import ranges_to_list


class Script(BaseScript):
    name = "Huawei.VRP.get_interfaces"
    interface = IGetInterfaces

    rx_iface_sep = re.compile(r"^(?:\s)?(\S+) current state\s*:\s*", re.MULTILINE)
    rx_line_proto = re.compile(
        r"Line protocol current state :\s*(?P<o_state>UP|DOWN)", re.IGNORECASE
    )
    rx_pvid = re.compile(r"PVID\s+:\s+(?P<pvid>\d+)")
    rx_inline_ifindex = re.compile(r"\(ifindex\s*:\s*(?P<ifindex>\d+)\)")
    rx_mtu = re.compile(r"The Maximum Transmit Unit is (?P<mtu>\d+)( bytes)?")
    rx_mac = re.compile(
        r"Hardware [Aa]ddress(?::| is) (?P<mac>[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4})"
    )
    rx_ipv4 = re.compile(
        r"Internet Address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})", re.IGNORECASE
    )
    rx_ipv4_unnumb = re.compile(
        r"Internet Address is unnumbered, using address of "
        r"(?P<iface>\S+\d+)\("
        r"(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})"
        r"\)",
        re.IGNORECASE,
    )
    rx_iftype = re.compile(r"^(\D+?|\d{2,3}\S+?)\d+.*$")
    rx_dis_ip_int = re.compile(
        r"^(?P<interface>\S+?)\s+current\s+state\s*:\s*(?:administratively\s+)?(?P<admin_status>up|down)",
        re.IGNORECASE,
    )
    rx_ip = re.compile(
        r"Internet Address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_ospf = re.compile(
        r"^Interface:\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\((?P<name>\S+)\)\s+",
        re.MULTILINE,
    )
    rx_ndp = re.compile(r"^\s*Interface: (?P<name>\S+)\s*\n^\s*Status: Enabled", re.MULTILINE)
    rx_ifindex = re.compile(
        r"^Name: (?P<name>\S+)\s*\n"
        r"^Physical IF Info:\s*\n"
        r"^\s*IfnetIndex: 0x(?P<ifindex>[0-9A-F]+)\s*\n",
        re.MULTILINE,
    )
    rx_lldp = re.compile(
        r"\n^\s*Interface\s(?P<name>\S+):\s*LLDP\sEnable\sStatus\s*:enabled.+\n", re.MULTILINE
    )

    rx_vlan_splitter = re.compile(r"(\d+\s+\S+\s+)", re.MULTILINE)
    rx_vlan_match = re.compile(r"(?P<vid>\d+)\s+(?P<type>\S+)\s+", re.MULTILINE)
    rx_vlan_switch_splitter = re.compile(r"(UT|TG|ST|MP):", re.MULTILINE)
    rx_iface_find = re.compile(r"\s*(?P<ifname>\S+)\s*\([UD]\)\s*")

    rx_vlan_port = re.compile(
        r"\s+VLAN\s+ID\s*:\s*(?P<vlan_id>\d+)\n"
        r"\s+VLAN\s+Type\s*:\s*(?P<vlan_type>\S+)\n"
        r"\s+Route\s+Interface\s*:\s*(?P<router_iface>.+|)\n"
        r"(?:\s+IP\s+Address\s*:\s*\S+\n)?(?:\s+Subnet\s+Mask\s*:\s*\S+\n)?"
        r"\s+Description\s*:\s*(?P<description>.+|)\n"
        r"\s+Name\s*:\s*(?P<name>.+|)\n"
        r"\s+Tagged\s+Ports\s*:(?:\s*|\snone)(?P<tagged_ports>(?:\n.+)+)\n"
        r"\s+Untagged\s+Ports\s*:(?:\s*|\snone)(?:(?P<untagged_ports>(?:\n.+)*))$",
        re.MULTILINE,
    )

    rx_vlan_port_check = re.compile(
        r"\s+Total\s+\d+\sVLAN\sexist\(s\)\s*\.\s*\n"
        r"\s+The\s+following\s+VLANs\s+exist\s*:\s*\n"
        r"\s+(\d+,\s*|\d+-\d+,\s*|\d+\(\S+\),\s*)+\s*(\S+)",
        re.MULTILINE,
    )

    rx_port_allow_vlan = re.compile(r"(?P<iface>\S+)\s+(?:trunking)\s+(?:\d)\s+(?P<vlans>\S+)")
    rx_port_port_vlan = re.compile(
        r"(?P<iface>\S+)\s+(?:trunking|hybrid|trunk|access)\s+(?:\d+)\s+(?P<vlans>.+)"
    )

    rx_vrrp = re.compile(
        r"(?P<vrid>\d+)\s+(?P<state>\w+)\s+(?P<ifname>\S+)\s+(?P<type>\w+)\s+(?P<virtual_ip>[0-9.]+)",
        re.MULTILINE,
    )
    rx_vrrp_ver_8_80 = re.compile(
        r"(?P<ifname>\S+)\s\|.+\nState\s+:\s(?P<status>\w+)\nVirtual IP\s+:\s(?P<virtual_ip>[0-9.]+)\s",
        re.MULTILINE,
    )

    def parse_displ_port_allow_vlan(self):
        # Used on CX200 series
        try:
            v = self.cli("display port allow-vlan")
        except self.CLISyntaxError:
            v = ""
        for iface, vlan in self.rx_port_allow_vlan.findall(v):
            yield iface, ranges_to_list(vlan)

    def parse_displ_port_vlan(self):
        # Used on Quidwai series switches
        try:
            v = self.cli("display port vlan")
        except self.CLISyntaxError:
            v = ""
        for iface, vlan in self.rx_port_port_vlan.findall(v):
            if not vlan.strip("- "):
                continue
            yield iface, ranges_to_list(vlan, None)

    def get_switchport_cli(self) -> DefaultDict[str, Dict[str, Union[int, list, None]]]:
        result = defaultdict(lambda: {"untagged": None, "tagged": []})
        try:
            if self.is_cloud_engine_switch:
                v = self.cli("display vlan", cached=True, allow_empty_response=False)
            else:
                v = self.cli("display vlan", cached=True)
        except self.CLISyntaxError:
            return result
        if self.rx_vlan_port_check.match(v):
            self.logger.info("Use 'display vlan all' command")
            v = self.cli("display vlan all")
            for block in v.split("\n\n"):
                match = self.rx_vlan_port.search(block)
                self.logger.debug("---------\n%s %s \n-----------\n", block, match)
                if not match:
                    continue
                for iface in match.group("tagged_ports").split():
                    result[iface]["tagged"] += [match.group("vlan_id")]
                for iface in match.group("untagged_ports").split():
                    result[iface]["untagged"] = match.group("vlan_id")
            return result
        rr = v.split("\n\n")
        switchports = ""
        if len(rr) == 3:
            _, switchports, _ = rr  # total info, mapping vlan interface table, vlans table
        elif len(rr) == 2:
            _, switchports, _ = rr[0], rr[1], []
        elif len(rr) == 1:
            # total = rr[0]
            pass
        vid = None
        for block in self.rx_vlan_splitter.split(switchports):
            if not block:
                continue
            elif self.rx_vlan_match.match(block):
                vid = int(self.rx_vlan_match.match(block).group("vid"))
                continue
            elif vid is None:
                continue
            key = None
            for switchport in self.rx_vlan_switch_splitter.split(block):
                if switchport.startswith("UT"):
                    key = "untagged"
                    continue
                elif switchport.startswith("TG"):
                    key = "tagged"
                    continue
                elif key is None:
                    continue
                for match in self.rx_iface_find.finditer(switchport):
                    # if key not in r[match.group("iface")]:
                    #     r[match.group("iface")][key] = []
                    ifname = self.profile.convert_interface_name(match.group("ifname"))
                    if key == "untagged":
                        result[ifname][key] = vid
                    else:
                        result[ifname][key] += [vid]
        if not result and self.is_quidway_S5xxx:
            self.logger.debug("Empty result. Use display port vlan")
            for iface, vlans in self.parse_displ_port_vlan():
                result[self.profile.convert_interface_name(iface)]["tagged"] += vlans
        if not result:
            self.logger.debug("Empty result. Use display port allow-vlan")
            for iface, vlans in self.parse_displ_port_allow_vlan():
                result[self.profile.convert_interface_name(iface)]["tagged"] += vlans
        return result

    def get_switchport(self) -> DefaultDict[int, Dict[str, Union[int, list, None]]]:
        result = defaultdict(lambda: {"tagged_vlans": [], "untagged_vlan": None})
        pid_ifindex_mappings = {}
        for port_num, ifindex, port_type, pvid in self.snmp.get_tables(
            [
                mib["HUAWEI-L2IF-MIB::hwL2IfPortIfIndex"],
                mib["HUAWEI-L2IF-MIB::hwL2IfPortType"],
                mib["HUAWEI-L2IF-MIB::hwL2IfPVID"],
            ],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            timeout=self.get_snmp_timeout(),
        ):
            pid_ifindex_mappings[port_num] = ifindex
            if not pvid:
                # Avoid zero-value untagged
                # Found on ME60-X8 5.160 (V600R008C10SPC300)
                continue
            result[ifindex]["untagged_vlan"] = pvid

        for oid, vlans_bank in self.snmp.getnext(
            mib["HUAWEI-L2IF-MIB::hwL2IfTrunkPortTable"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            display_hints={mib["HUAWEI-L2IF-MIB::hwL2IfTrunkPortTable"]: render_bin},
            timeout=self.get_snmp_timeout(),
        ):
            oid, port_num = oid.rsplit(".", 1)
            if oid.endswith("1.3"):
                # HighVLAN
                # start = 2048
                vlans = range(2048, 4096)
            else:
                vlans = range(0, 2048)
            result[pid_ifindex_mappings[port_num]]["tagged_vlans"] += list(
                compress(
                    vlans,
                    [
                        int(x)
                        for x in chain.from_iterable("{0:08b}".format(mask) for mask in vlans_bank)
                    ],
                )
            )
        return result

    def get_ospfint(self):
        if not (
            self.has_capability("Network | OSFP | v2") or self.has_capability("Network | OSFP | v3")
        ):
            return []
        try:
            v = self.cli("display ospf interface all")
        except self.CLISyntaxError:
            return []
        ospfs = []
        for s in v.split("\n"):
            match = self.rx_ospf.search(s)
            if match:
                ospfs += [match.group("name")]
        return ospfs

    def get_ndpint(self):
        if not self.has_capability("Huawei | NDP"):
            return []
        try:
            v = self.cli("display ndp", cached=True)
        except self.CLISyntaxError:
            return []
        ndp = []
        for match in self.rx_ndp.finditer(v):
            ndp += [match.group("name")]
        return ndp

    def get_ifindex(self):
        try:
            v = self.cli("display rm interface")
        except self.CLISyntaxError:
            return {}
        ifindex = {}
        for match in self.rx_ifindex.finditer(v):
            ifindex[match.group("name")] = match.group("ifindex")
        return ifindex

    def get_stpint(self):
        try:
            v = self.cli("display stp brief", cached=True)
        except self.CLISyntaxError:
            return {}
        if "Protocol Status    :disabled" in v:
            return {}
        stp = []
        for line in v.splitlines():
            if not line:
                continue
            stp += [line.split()[1]]
        if stp:
            stp.pop(0)
        return stp

    def get_lldpint(self):
        try:
            v = self.cli("display lldp local", cached=True)
        except self.CLISyntaxError:
            return {}
        lldp = []
        for match in self.rx_lldp.finditer(v):
            lldp += [match.group("name")]
        return lldp

    def get_mpls_vpn(self):
        imap = {}  # interface -> VRF
        vrfs = {"default": {"forwarding_instance": "default", "type": "ip", "interfaces": []}}
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            vrfs[v["name"]] = {
                "forwarding_instance": v["name"],
                "type": v["type"],
                "interfaces": [],
            }
            rd = v.get("rd")
            if rd:
                vrfs[v["name"]]["rd"] = rd
            vpn_id = v.get("vpn_id")
            if vpn_id:
                vrfs[v["name"]]["vpn_id"] = vpn_id
            for i in v["interfaces"]:
                imap[i] = v["name"]
        return vrfs, imap

    def get_vrrpint(self):
        if not (
            self.has_capability("Network | HSRP")
            or self.has_capability("Network | VRRP | v2")
            or self.has_capability("Network | VRRP | v3")
        ):
            return {}
        try:
            v = self.cli("display vrrp brief", cached=True)
            rx_vrrp = self.rx_vrrp
        except self.CLISyntaxError:
            try:
                v = self.cli("display vrrp verbose", cached=True)
                rx_vrrp = self.rx_vrrp_ver_8_80
            except self.CLISyntaxError:
                return {}
        vrrps = {}
        for match in rx_vrrp.finditer(v):
            ifname = self.profile.convert_interface_name(match.group("ifname"))
            if ifname in vrrps:
                vrrps[ifname] += [match.group("virtual_ip") + "/32"]
            else:
                vrrps[ifname] = [match.group("virtual_ip") + "/32"]
        return vrrps

    def execute_cli(self):
        # Clear output after previous script
        self.cli("")
        # Get switchports and fill tagged/untagged lists if they are not empty
        switchports = self.get_switchport_cli()
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        # Get IPv4 interfaces
        ipv4_interfaces = defaultdict(list)  # interface -> [ipv4 addresses]
        c_iface = None
        for line in self.cli("display ip interface").splitlines():
            match = self.rx_dis_ip_int.search(line)
            if match:
                c_iface = self.profile.convert_interface_name(match.group("interface"))
                continue
            # Primary ip
            match = self.rx_ip.search(line)
            if not match:
                continue
            ip = match.group("ip")
            ipv4_interfaces[c_iface] += [ip]
        #
        interfaces = {}
        # Get OSPF interfaces
        ospfs = self.get_ospfint()
        # Get NDP interfaces
        ndps = self.get_ndpint()
        # Get ifindexes
        ifindexes = self.get_ifindex()
        # Get STP interfaces
        stps = self.get_stpint()
        # Get LLDP interfaces
        lldps = self.get_lldpint()
        # Get VRRP interfaces
        vrrps = self.get_vrrpint()

        v = self.cli("display interface", cached=True)
        il = self.rx_iface_sep.split(v)[1:]
        for full_ifname, data in zip(il[::2], il[1::2]):
            ifname = self.profile.convert_interface_name(full_ifname)
            if ifname.startswith("NULL"):
                continue
            # I do not known, what are these
            if ifname.startswith("DCN-Serial") or ifname.startswith("Cpos-Trunk"):
                continue
            sub = {
                "name": ifname,
                "admin_status": True,
                "oper_status": True,
                "enabled_protocols": [],
                "enabled_afi": [],
            }
            if ifname in switchports and ifname not in portchannel_members:
                # Bridge
                sub["enabled_afi"] += ["BRIDGE"]
                u, t = switchports[ifname]["untagged"], switchports[ifname].get("tagged")
                if u:
                    sub["untagged_vlan"] = u
                if t:
                    sub["tagged_vlans"] = t
            elif ifname in ipv4_interfaces:
                # IPv4
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = ipv4_interfaces[ifname]
            if ifname in ospfs:
                # OSPF
                sub["enabled_protocols"] += ["OSPF"]
            if ifname.lower().startswith("vlanif"):
                # SVI
                sub["vlan_ids"] = [int(ifname[6:].strip())]
            if ifname.lower().startswith("vlan-interface"):
                # SVI
                sub["vlan_ids"] = [int(ifname[14:].strip())]
            # Parse data
            ifindex = self.rx_inline_ifindex.search(data)
            a_stat, data = data.split("\n", 1)
            a_stat = a_stat.lower().endswith("up")
            o_stat = None
            for line in data.splitlines():
                line = line.strip()
                # Oper. status
                if o_stat is None:
                    match = self.rx_line_proto.search(line)
                    if match:
                        o_stat = match.group("o_state").lower().endswith("up")
                        continue
                # Process description
                if line.startswith("Description:"):
                    d = line[12:].strip()
                    if d != "---":
                        sub["description"] = d
                    continue
                # Process description
                if line.startswith("Description :"):
                    d = line[13:].strip()
                    if d != "---":
                        sub["description"] = d
                    continue
                # MAC
                if not sub.get("mac"):
                    match = self.rx_mac.search(line)
                    if match and match.group("mac") != "0000-0000-0000":
                        sub["mac"] = match.group("mac")
                        continue
                # Static vlans
                match = self.rx_pvid.search(line)
                if match and "untagged_vlan" not in sub:
                    sub["untagged_vlan"] = int(match.group("pvid"))
                    if "BRIDGE" not in sub["enabled_afi"]:
                        sub["enabled_afi"] += ["BRIDGE"]
                    continue
                # Static vlans
                if line.startswith("Encapsulation "):
                    enc = line[14:]
                    if enc.startswith("802.1Q"):
                        sub["vlan_ids"] = [enc.split(",")[2].split()[2]]
                    continue
                # MTU
                match = self.rx_mtu.search(line)
                if match:
                    sub["mtu"] = int(match.group("mtu"))
                    continue
                # IP Unnumbered
                match = self.rx_ipv4_unnumb.search(line)
                if match:
                    sub["ip_unnumbered_subinterface"] = match.group("iface")
                    sub["enabled_afi"] = ["IPv4"]
                    continue
            if "." not in ifname:
                if o_stat is None:
                    o_stat = False
                match = self.rx_iftype.match(ifname)
                iftype = self.profile.get_interface_type(match.group(1))
                if iftype is None:
                    self.logger.info("Iface name %s, type unknown", match.group(1))
                    continue  # Skip ignored interfaces
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": iftype,
                    "enabled_protocols": [],
                    "subinterfaces": [sub],
                }
                if ifname in ifindexes:
                    iface["snmp_ifindex"] = int(ifindexes[ifname], 16)
                elif ifindex:
                    iface["snmp_ifindex"] = int(ifindex.group("ifindex"))
                if "mac" in sub:
                    iface["mac"] = sub["mac"]
                if "description" in sub:
                    iface["description"] = sub["description"]
                if ifname in ndps:
                    # NDP
                    iface["enabled_protocols"] += ["NDP"]
                if ifname in stps:
                    # STP
                    iface["enabled_protocols"] += ["STP"]
                if ifname in lldps:
                    # LLDP
                    iface["enabled_protocols"] += ["LLDP"]
                if ifname in vrrps.keys():
                    # VRRP
                    sub["enabled_protocols"] += ["VRRP"]
                    sub["ipv4_addresses"] += vrrps[ifname]
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["subinterfaces"] = []
                    if is_lacp:
                        iface["enabled_protocols"] += ["LACP"]
                interfaces[ifname] = iface
            else:
                if ifindex:
                    sub["snmp_ifindex"] = int(ifindex.group("ifindex"))
                ifname, vlan_id = ifname.split(".")
                if is_vlan(vlan_id):
                    sub["vlan_ids"] = [vlan_id]
                interfaces[ifname]["subinterfaces"] += [sub]
        # VRF and forwarding_instance proccessed
        vrfs, vrf_if_map = self.get_mpls_vpn_mappings()
        for i in interfaces.keys():
            iface_vrf = "default"
            subs = interfaces[i]["subinterfaces"]
            interfaces[i]["subinterfaces"] = []
            if i in vrf_if_map:
                iface_vrf = vrf_if_map[i]
                vrfs[vrf_if_map[i]]["interfaces"] += [interfaces[i]]
            else:
                vrfs["default"]["interfaces"] += [interfaces[i]]
            for s in subs:
                if s["name"] in vrf_if_map and vrf_if_map[s["name"]] != iface_vrf:
                    vrfs[vrf_if_map[s["name"]]]["interfaces"] += [
                        {
                            "name": s["name"],
                            "type": "other",
                            "enabled_protocols": [],
                            "subinterfaces": [s],
                        }
                    ]
                else:
                    interfaces[i]["subinterfaces"] += [s]
        return list(vrfs.values())
