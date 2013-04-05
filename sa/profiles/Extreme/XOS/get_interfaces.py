# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    """
    Extreme.XOS.get_interfaces
    """
    name = "Extreme.XOS.get_interfaces"
    implements = [IGetInterfaces]

    rx_vlan = re.compile(r"^VLAN Interface.*\s+with\s+name\s+(?P<name>.+?)\s+created.+$",
        re.IGNORECASE | re.MULTILINE)
    rx_untag = re.compile(r"^Tagging:\s+Untagged.*$",
        re.IGNORECASE | re.MULTILINE)
    rx_tag = re.compile(r"^.*Tagging:\s+802.1Q\s+Tag\s+(?P<tag>\d+)\s*$",
        re.IGNORECASE | re.MULTILINE)
    rx_ip = re.compile(r"^IP:\s+(?P<ip>\S+)/(?P<mask>\S+).*$",
        re.IGNORECASE | re.MULTILINE)
    rx_tagged = re.compile(r"^Tag(?:ged)?:\s+(?P<ifaces>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE)
    rx_untagged = re.compile(r"^Untag:\s+(?P<ifaces>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE)
    rx_port_descr = re.compile(r"\(([^)]+)\)")
    rx_port_name = re.compile("(?P<port>\d+:\d+)")
    rx_port_name1 = re.compile("(?P<port>\d+)")

    def execute(self):
        vlans = []
        current = {}
        self.descriptions = {}  # port -> descriptions
        self.ports = set()  # All ports
        v = self.cli("show vlan detail")
        v = v.replace(",\n", ",")
        il_parse = self.parse_interfaces1
        for l in v.splitlines():
            l = l.strip()
            # Process VLAN name
            match = self.rx_vlan.match(l)
            if match:
                # Save current vlan
                if current:
                    vlans += [current]
                # New VLAN
                name = match.group("name").strip()
                if name[0] == name[-1] and name[0] == "\"":
                    name = name[1:-1].strip()
                current = {
                    "name": name,
                    "tagged": [],
                    "untagged": []
                }
                continue
            # Process VLAN tag
            match = self.rx_untag.match(l)
            if match:
                # Disabled vlan
                current = {}
                continue
            # Process VLAN tag
            match = self.rx_tag.match(l)
            if match:
                if l.startswith("Admin"):
                    il_parse = self.parse_interfaces2
                current["vlan_id"] = int(match.group("tag"))
                continue
            # Process IP
            match = self.rx_ip.match(l)
            if match:
                mask = IPv4.netmask_to_len(match.group("mask"))
                current["ip"] = "%s/%d" % (match.group("ip"), mask)
                continue
            # Process tagged
            match = self.rx_tagged.match(l)
            if match:
                current["tagged"] += il_parse(match.group("ifaces"))
                continue
            # Process untagged
            match = self.rx_untagged.match(l)
            if match:
                current["untagged"] += il_parse(match.group("ifaces"))
                continue
        # Save last VLAN
        if current:
            vlans += [current]
        # Process parsed data
        interfaces = []
        # port -> vlan mappings
        untagged = defaultdict(list)
        tagged = defaultdict(list)
        # Process vlans interfaces
        for v in vlans:
            vid = v["vlan_id"]
            # SVI interface
            if v.get("ip"):
                interfaces += [{
                    "name": v["name"],
                    "type": "SVI",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{
                        "name": v["name"],
                        "admin_status": True,
                        "oper_status": True,
                        "vlan_ids": [v["vlan_id"]],
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [v["ip"]]
                    }]
                }]
            # Fill port->vlan mappings
            for p in v["untagged"]:
                untagged[p] += [vid]
            for p in v["tagged"]:
                tagged[p] += [vid]
        # Process ports
        for p in sorted(self.ports):
            si = {
                "name": p,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"]
            }
            if p in untagged:
                si["untagged_vlan"] = untagged[p][0]
            if p in tagged:
                si["tagged_vlans"] = tagged[p]
            if p in self.descriptions:
                si["description"] = self.descriptions[p]
            i = {
                "name": p,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [si]
            }
            if p in self.descriptions:
                i["description"] = self.descriptions[p]
                si["description"] = self.descriptions[p]
            interfaces += [i]
        # Return
        return [{"interfaces": interfaces}]

    def parse_interfaces1(self, l):
        # Fetch ports
        ports = set()
        for i in self.rx_port_descr.split(l):
            match = self.rx_port_name.search(i)
            if match:
                port = match.group("port")
                ports.add(port)
                self.ports.add(port)
        # Fetch descriptions
        for match in self.rx_port_descr.finditer(l):
            d = match.group(1)
            if ":" in d:
                p, d = d.split(":", 1)
                p = p.replace("-", ":")
                self.descriptions[p] = d
        return list(ports)

    def parse_interfaces2(self, l):
        ports = set()
        for p in l.split(","):
            p = p.strip()
            # split description
            match = self.rx_port_descr.search(p)
            if match:
                d = match.group(1)
                if "-" in d:
                    d = d.split("-", 1)[1]
                    p = p[:match.start()]
                self.descriptions[p] = d
            match = self.rx_port_name1.search(p)
            if match:
                ports.add(match.group("port"))
        self.ports.update(ports)
        return list(ports)
