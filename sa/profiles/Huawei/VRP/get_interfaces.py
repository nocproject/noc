# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    name = "Huawei.VRP.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 240

    rx_iface_sep = re.compile(r"^(\S+) current state\s*:\s+",
                              re.MULTILINE)
    rx_line_proto = re.compile(
        r"Line protocol current state : (?P<o_state>UP|DOWN)",
        re.IGNORECASE
    )
    rx_mac = re.compile(
        "Hardware address is (?P<mac>[0-9af]{4}-[0-9a-f]{4}-[0-9a-f]{4})"
    )
    rx_ipv4 = re.compile(
        r"Internet Address is (?P<ip>\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2}/\d{1,2})",
        re.IGNORECASE
    )

    rx_iftype = re.compile(r"^(\S+?)\d+.*$")

    rx_dis_ip_int = re.compile(r"^(?P<interface>\S+?)\s+current\s+state\s+:\s+(?:administratively\s+)?(?P<admin_status>up|down)", re.IGNORECASE)

    rx_ip = re.compile(r"Internet Address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})", re.MULTILINE | re.IGNORECASE)

    rx_ospf = re.compile(r"^Interface:\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\((?P<name>\S+)\)\s+", re.MULTILINE)

    types = {
        "Aux": "physical",
        "Eth-Trunk": "aggregated",
        "Ip-Trunk": "aggregated",
        "XGigabitEthernet": "physical",
        "GigabitEthernet": "physical",
        "FastEthernet": "physical",
        "Ethernet": "physical",
        "Logic-Channel": "tunnel",
        "LoopBack": "loopback",
        "MEth": "management",
        "M-Ethernet": "management",
        "Ring-if": "physical",
        "Tunnel": "tunnel",
        "Virtual-Template": None,
        "Vlanif": "SVI"
    }

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

    def execute(self):
        # Get switchports and fill tagged/untagged lists if they are not empty
        switchports = {}
        for sp in self.scripts.get_switchport():
            switchports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"]
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
        interfaces = []
        # Get OSPF interfaces
        ospfs = self.get_ospfint()

        v = self.cli("display interface")
        il = self.rx_iface_sep.split(v)[1:]
        for full_ifname, data in zip(il[::2], il[1::2]):
            ifname = self.profile.convert_interface_name(full_ifname)
            if ifname.startswith("NULL"):
                continue
            sub = {
                "name": ifname,
                "admin_status": True,
                "oper_status": True,
                "enabled_protocols": [],
                "enabled_afi": []
            }
            if (ifname in switchports and
                        ifname not in portchannel_members):
                # Bridge
                sub["enabled_afi"] += ['BRIDGE']
                u, t = switchports[ifname]
                if u:
                    sub["untagged_vlan"] = u
                if t:
                    sub["tagged_vlans"] = t
            elif ifname in ipv4_interfaces:
                # IPv4
                sub["enabled_afi"] = ['IPv4']
                sub["ipv4_addresses"] = ipv4_interfaces[ifname]
            if ifname in ospfs:
                # OSPF
                sub["enabled_protocols"] += ["OSPF"]
            if ifname.lower().startswith("vlanif"):
                # SVI
                sub["vlan_ids"] = [int(ifname[6:].strip())]
            # Parse data
            a_stat, data = data.split("\n", 1)
            a_stat = a_stat.lower().endswith("up")
            o_stat = None
            for l in data.splitlines():
                # Oper. status
                if o_stat is None:
                    match = self.rx_line_proto.search(l)
                    if match:
                        o_stat = match.group("o_state").lower().endswith("up")
                        continue
                # Process description
                if l.startswith("Description:"):
                    d = l[12:].strip()
                    if d != "---":
                        sub["description"] = d
                    continue
                # MAC
                if not sub.get("mac"):
                    match = self.rx_mac.search(l)
                    if match:
                        sub["mac"] = match.group("mac")
                        continue
                # Static vlans
                if l.startswith("Encapsulation "):
                    enc = l[14:]
                    if enc.startswith("802.1Q"):
                        sub["vlan_ids"] = [enc.split(",")[2].split()[2]]
                    continue
            if "." not in ifname:
                if o_stat is None:
                    o_stat = False
                match = self.rx_iftype.match(ifname)
                iftype = self.types[match.group(1)]
                if iftype is None:
                    continue  # Skip ignored interfaces
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": iftype,
                    "enabled_protocols": [],
                    "subinterfaces": [sub]
                }
                if "mac" in sub:
                    iface["mac"] = sub["mac"]
                if "description" in sub:
                    iface["description"] = sub["description"]
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["subinterfaces"] = []
                    if is_lacp:
                        iface["enabled_protocols"] += ["LACP"]
                interfaces += [iface]
            else:
                interfaces[-1]["subinterfaces"] += [sub]
        # Process VRFs
        vrfs = {
            "default": {
                "forwarding_instance": "default",
                "type": "ip",
                "interfaces": []
            }
        }
        imap = {}  # interface -> VRF
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            if v["type"] == "VRF":
                vrfs[v["name"]] = {
                    "forwarding_instance": v["name"],
                    "type": "VRF",
                    "interfaces": []
                }
                rd = v.get("rd")
                if rd:
                    vrfs[v["name"]]["rd"] = rd
                for i in v["interfaces"]:
                    imap[i] = v["name"]
        for i in interfaces:
            subs = i["subinterfaces"]
            if subs:
                for vrf in set(imap.get(si["name"], "default") for si in subs):
                    c = i.copy()
                    c["subinterfaces"] = [si for si in subs
                                          if imap.get(si["name"], "default") == vrf]
                    vrfs[vrf]["interfaces"] += [c]
            elif i.get("aggregated_interface"):
                vrfs["default"]["interfaces"] += [i]
        return vrfs.values()
