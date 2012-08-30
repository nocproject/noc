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

    rx_dis_int = re.compile(r"^(?P<interface>\S+?)\s+current\s+state\s+:\s+(?:administratively\s+)?(?P<admin_status>up|down)\n"
                            r"(?:Line\s+protocol\s+current\s+state\s+:\s+(?P<oper_status>up|down)\n)?"
                            r"(?:Last line protocol up time :[^\n]+\n)?"
                            r"(?:Description\s*:\s*(?P<desc>[^\n,]+)(?:, (?:Switch|Router) Port)?\n)?"
                            r"(?:(?:Route|Switch) Port[^\n]+\n)?"
                            r"(?:PVID[^\n]+\n)?" # vrp v5.3
                            r"(?:The Maximum Transmit Unit[^\n]+\n)?" # vrp v5.3
                            r"(?:Internet protocol processing[^\n]+\n)?" # vrp v5.3
                            r"(?:Internet address ((is\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}))|([^\d]+))\n)?"
                            r"IP Sending Frames\' Format is\s+\w+,\s+Hardware\s+(?P<hardw>[^\n]+)\n"
                            r"(?:Encapsulation\s+(?P<encaps>[^\n]))?",
                            re.MULTILINE | re.IGNORECASE)

    rx_dis_ip_int = re.compile(r"^(?P<interface>\S+?)\s+current\s+state\s+:\s+(?:administratively\s+)?(?P<admin_status>up|down)", re.IGNORECASE)
    rx_mac = re.compile(r"address\sis\s(?P<mac>\w{4}\.\w{4}\.\w{4})", re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(r"Internet Address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})", re.MULTILINE | re.IGNORECASE)
    #rx_sec_ip = re.compile(r"Internet Address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}) Sub", re.MULTILINE | re.IGNORECASE)
    rx_ospf = re.compile(r"^Interface:\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\((?P<name>\S+)\)\s+", re.MULTILINE)
    rx_huawei_interface_name = re.compile(r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+)?)?([.:]\d+(\.\d+)?)?)$", re.IGNORECASE)

    types = {
        "Aux": "physical",
        "Eth-Trunk": "aggregated",
        "Ip-Trunk": "aggregated",
        "GigabitEthernet": "physical",
        "Logic-Channel": "tunnel",
        "LoopBack": "loopback",
        "MEth": "management",
        "M-Ethernet": "management",
        "Ring-if": "physical",
        "Tunnel": "tunnel",
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
        for match in self.rx_dis_int.finditer(v):
            full_ifname = match.group("interface")
            ifname = self.profile.convert_interface_name(full_ifname)

            if ifname in ["NULL"]:
                continue

            a_stat = match.group("admin_status").lower() == "up"
            if match.group("oper_status"):
                o_stat = match.group("oper_status").lower() == "up"
            else:
                o_stat = a_stat

            hw = match.group("hardw")

            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
            }

            if match.group("desc"):
                sub["description"] = match.group("desc")

            matchmac = self.rx_mac.search(hw)
            if matchmac:
                sub["mac"] = matchmac.group("mac")

            if ifname in switchports and ifname not in portchannel_members:
                sub["is_bridge"] = True
                u, t = switchports[ifname]
                if u:
                    sub["untagged_vlan"] = u
                if t:
                    sub["tagged_vlans"] = t

            # Static vlans
            if match.group("encaps"):
                encaps = match.group("encaps")
                if encaps[:6] == "802.1Q":
                    sub["vlan_ids"] = [encaps.split(",")[2].split()[2]]

            # IPv4
            if match.group("ip"):
                if ifname in ipv4_interfaces:
                    sub["is_ipv4"] = True
                    sub["ipv4_addresses"] = ipv4_interfaces[ifname]
            if ifname in ospfs:
                sub["is_ospf"] = True

            if "." not in ifname:
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": self.types[re.sub(r'\d.*', "", ifname)],
                    "subinterfaces": [sub]
                }
                if match.group("desc"):
                    iface["description"] = match.group("desc")

                if "mac" in sub:
                    iface["mac"] = sub["mac"]
                # Set VLAN IDs for SVI
                if iface["type"] == "SVI":
                    sub["vlan_ids"] = [int(ifname[6:].strip())]
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["is_lacp"] = is_lacp
                interfaces += [iface]
            else:
                # Append additional subinterface
                try:
                    interfaces[-1]["subinterfaces"] += [sub]
                except KeyError:
                    interfaces[-1]["subinterfaces"] = [sub]

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
            for vrf in set(imap.get(si["name"], "default") for si in subs):
                c = i.copy()
                c["subinterfaces"] = [si for si in subs
                                      if imap.get(si["name"], "default") == vrf]
                vrfs[vrf]["interfaces"] += [c]
        return vrfs.values()
