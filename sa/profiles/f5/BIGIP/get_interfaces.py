# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from collections import defaultdict
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    name = "f5.BIGIP.get_interfaces"
    cache = True
    implements = [IGetInterfaces]

    rx_self = re.compile(r"^net self \S+ {", re.MULTILINE | re.DOTALL)
    rx_self_a = re.compile(
        r"^\s+address\s+(?P<address>\S+).+"
        r"^\s+vlan\s+(?P<vlan>\S+)",
        re.DOTALL | re.MULTILINE)

    def parse_kv(self, s):
        r = {}
        for l in s.splitlines():
            k, v = l.rsplit(" ", 1)
            r[k.strip()] = v
        return r

    def execute(self):
        r = []
        # Get self ip
        addresses = defaultdict(list)
        v = self.cli("list /net self")
        for data in self.rx_self.split(v):
            match = self.rx_self_a.search(data)
            if match:
                addresses[match.group("vlan")] += [match.group("address")]
        # Get VLAN mappings
        vlans = {}  # tag -> data
        trunks = {}  # name -> [members]
        aggregated = {}  # name -> aggregated interface
        current_vlan = None
        current_trunk = None
        lacp_interfaces = set()
        interfaces = set()
        v = self.cli("show /net vlan")
        for h, data in self.parse_blocks(v):
            if h.startswith("Net::Vlan: "):
                d = self.parse_kv(data)
                name = h[11:]
                current_vlan = {
                    "name": name,
                    "mac": d.get("Mac Address (True)"),
                    "mtu": d.get("MTU"),
                    "tag": d.get("Tag"),
                    "tagged": [],
                    "untagged": [],
                    "ipv4_addresses": [a for a in addresses[name]
                                       if ":" not in a],
                    "ipv6_addresses": [a for a in addresses[name]
                                       if ":" in a]
                }
                vlans[name] = current_vlan
                current_trunk = None
            elif h.startswith("Net::Vlan-Member: "):
                name = h[18:]
                d = self.parse_kv(data)
                tagged = d.get("Tagged") == "yes"
                if tagged:
                    current_vlan["tagged"] += [name]
                else:
                    current_vlan["untagged"] += [name]
                interfaces.add(name)
            elif h.startswith("Net::Trunk"):
                name = data.splitlines()[0].split(" ", 1)[0]
                current_trunk = {
                    "name": name,
                    "members": []
                }
                trunks[name] = current_trunk
                interfaces.add(name)
            elif h.startswith("Net::Interface"):
                if current_trunk:
                    for l in data.splitlines():
                        i = l.split(" ", 1)[0]
                        current_trunk["members"] += [i]
                        interfaces.add(i)
                        aggregated[i] = current_trunk["name"]
            elif h.startswith("Net::LACP Status (interface: "):
                name = h[29:-1]
                lacp_interfaces.add(name)
        # Build result
        ifaces = []
        tagged = defaultdict(list)  # interface -> [vlans]
        untagged = {}  # interface -> vlan
        for vlan in vlans:
            # SVI
            v = vlans[vlan]
            enabled_afi = []
            tag = int(v["tag"])
            if v["ipv4_addresses"]:
                enabled_afi += ["IPv4"]
            if v["ipv6_addresses"]:
                enabled_afi += ["IPv6"]
            if enabled_afi:
                iface = {
                    "name": v["name"],
                    "type": "SVI",
                    "mac": v["mac"],
                    "mtu": v["mtu"],
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{
                        "name": v["name"],
                        "vlan_ids": [tag],
                        "enabled_afi": enabled_afi,
                        "ipv4_addresses": v["ipv4_addresses"],
                        "ipv6_addresses": v["ipv6_addresses"],
                        "admin_status": True,
                        "oper_status": True,
                    }]
                }
                ifaces += [iface]
            for i in v["tagged"]:
                tagged[i] += [tag]
            for i in v["untagged"]:
                untagged[i] = tag
        for i in interfaces:
            itype = "physical" if i not in trunks else "aggregated"
            iface = {
                "name": i,
                "type": itype,
                # "mac": v["mac"],
                # "mtu": v["mtu"],
                "admin_status": True,
                "oper_status": True,
                "enabled_protocols": [],
                "subinterfaces": []
            }
            if i in tagged or i in untagged:
                si = {
                    "name": i,
                    "enabled_afi": ["BRIDGE"],
                    "admin_status": True,
                    "oper_status": True,
                }
                if i in tagged:
                    si["tagged_vlans"] = sorted(tagged[i])
                if i in untagged:
                    si["untagged_vlan"] = untagged[i]
                iface["subinterfaces"] = [si]
            if i in lacp_interfaces:
                iface["enabled_protocols"] += ["LACP"]
            if i in aggregated:
                iface["aggregated_interface"] = aggregated[i]
            ifaces += [iface]
        return [{"interfaces": sorted(ifaces, key=lambda x: x["name"])}]
