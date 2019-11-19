# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
import time
from collections import defaultdict

# Third-party modules
import six

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.validators import is_vlan


class Script(BaseScript):
    name = "Huawei.VRP.get_interfaces"
    interface = IGetInterfaces

    rx_iface_sep = re.compile(r"^(?:\s)?(\S+) current state\s*:\s*", re.MULTILINE)
    rx_line_proto = re.compile(
        r"Line protocol current state :\s*(?P<o_state>UP|DOWN)", re.IGNORECASE
    )
    rx_pvid = re.compile(r"PVID\s+:\s+(?P<pvid>\d+)")
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
    rx_ndp = re.compile(r"^\s*Interface: (?P<name>\S+)\s*\n" r"^\s*Status: Enabled", re.MULTILINE)
    rx_ifindex = re.compile(
        r"^Name: (?P<name>\S+)\s*\n"
        r"^Physical IF Info:\s*\n"
        r"^\s*IfnetIndex: 0x(?P<ifindex>[0-9A-F]+)\s*\n",
        re.MULTILINE,
    )
    rx_lldp = re.compile(
        r"\n^\s*Interface\s(?P<name>\S+):" r"\s*LLDP\sEnable\sStatus\s*:enabled.+\n", re.MULTILINE
    )

    def get_ospfint(self):
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
        try:
            v = self.cli("display ndp")
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
            v = self.cli("display stp brief")
        except self.CLISyntaxError:
            return {}
        if "Protocol Status    :disabled" in v:
            return {}
        stp = []
        for l in v.splitlines():
            if not l:
                continue
            stp += [l.split()[1]]
        stp.pop(0)
        return stp

    def get_lldpint(self):
        try:
            v = self.cli("display lldp local")
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

    def execute_snmp(self):
        vlans = self.scripts.get_switchport()
        r = super(Script, self).execute_snmp()
        if vlans:
            vlans = {
                v["interface"]: {"untagged": v.get("untagged"), "tagged": v.get("tagged", [])}
                for v in vlans
            }
            for fi in r:
                for iface in fi["interfaces"]:
                    if iface["name"] in vlans:
                        if vlans[iface["name"]]["untagged"]:
                            iface["subinterfaces"][0]["untagged_vlan"] = vlans[iface["name"]][
                                "untagged"
                            ]
                        iface["subinterfaces"][0]["tagged_vlans"] = vlans[iface["name"]]["tagged"]
        time.sleep(2)
        vrfs, imap = self.get_mpls_vpn()
        if imap:
            for fi in r:
                for iface in fi["interfaces"]:
                    subs = iface["subinterfaces"]
                    for vrf in set(imap.get(si["name"], "default") for si in subs):
                        c = iface.copy()
                        c["subinterfaces"] = [
                            si for si in subs if imap.get(si["name"], "default") == vrf
                        ]
                        vrfs[vrf]["interfaces"] += [c]
            return list(six.itervalues(vrfs))
        return r

    def execute_cli(self):
        # Get switchports and fill tagged/untagged lists if they are not empty
        switchports = {}
        for sp in self.scripts.get_switchport():
            switchports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"],
            )
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
        for l in self.cli("display ip interface").splitlines():
            match = self.rx_dis_ip_int.search(l)
            if match:
                c_iface = self.profile.convert_interface_name(match.group("interface"))
                continue
            # Primary ip
            match = self.rx_ip.search(l)
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
                u, t = switchports[ifname]
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
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["subinterfaces"] = []
                    if is_lacp:
                        iface["enabled_protocols"] += ["LACP"]
                interfaces[ifname] = iface
            else:
                ifname, vlan_id = ifname.split(".")
                if is_vlan(vlan_id):
                    sub["vlan_ids"] = [vlan_id]
                interfaces[ifname]["subinterfaces"] += [sub]
        # Process VRFs
        vrfs = {"default": {"forwarding_instance": "default", "type": "ip", "interfaces": []}}
        imap = {}  # interface -> VRF
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            vrfs[v["name"]] = {
                "forwarding_instance": v["name"],
                "type": v["type"],
                "vpn_id": v.get("vpn_id"),
                "interfaces": [],
            }
            rd = v.get("rd")
            if rd:
                vrfs[v["name"]]["rd"] = rd
            for i in v["interfaces"]:
                imap[i] = v["name"]
        for i in interfaces.keys():
            iface_vrf = "default"
            subs = interfaces[i]["subinterfaces"]
            interfaces[i]["subinterfaces"] = []
            if i in imap:
                iface_vrf = imap[i]
                vrfs[imap[i]]["interfaces"] += [interfaces[i]]
            else:
                vrfs["default"]["interfaces"] += [interfaces[i]]
            for s in subs:
                if s["name"] in imap and imap[s["name"]] != iface_vrf:
                    vrfs[imap[s["name"]]]["interfaces"] += [
                        {
                            "name": s["name"],
                            "type": "other",
                            "enabled_protocols": [],
                            "subinterfaces": [s],
                        }
                    ]
                else:
                    interfaces[i]["subinterfaces"] += [s]
        return list(six.itervalues(vrfs))
