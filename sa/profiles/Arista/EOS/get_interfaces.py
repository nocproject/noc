# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    name = "Arista.EOS.get_interfaces"
    implements = [IGetInterfaces]

    type_map = {
        "et": "physical",
        "ma": "management",
        "vl": "SVI",
        "po": "aggregated"
    }

    rx_iface_sep = re.compile(r"^(\S+\d+)\s+is\s+.+$", re.MULTILINE)
    rx_hw_mac = re.compile(
        r"^\s+Hardware is \S+, address is (?P<mac>\S+)"
    )
    rx_description = re.compile(
        r"^\s+Description:\s+(?P<description>.+)"
    )
    rx_member = re.compile(
        r"^\s+Member of (?P<agg>\S+)"
    )
    rx_ip = re.compile(
        r"^\s+Internet address is (?P<ip>\S+)"
    )

    def execute(self, interface=None):
        interfaces = []
        # Prepare switchports
        sw = {}  # Name -> untagged, tagged
        for l in self.scripts.get_switchport():
            sw[l["interface"]] = (l.get("untagged"), l.get("tagged", []))
        #
        v = self.cli("show interfaces")
        il = self.rx_iface_sep.split(v)[1:]
        # Merge interface names and data together
        for name, data in zip(il[::2], il[1::2]):
            name = self.profile.convert_interface_name(name)
            iface = {
                "name": name,
                "type": self.type_map[name[:2].lower()],
                # admin status
                # oper status
                "subinterfaces": []
            }
            ip = None
            for l in data.splitlines():
                # Get MAC addres
                if not iface.get("mac"):
                    match = self.rx_hw_mac.match(l)
                    if match:
                        iface["mac"] = match.group("mac")
                        continue
                # Get description
                if not iface.get("description"):
                    match = self.rx_description.match(l)
                    if match:
                        iface["description"] = match.group("description")
                        continue
                if not iface.get("aggregated_interface"):
                    match = self.rx_member.match(l)
                    if match:
                        iface["aggregated_interface"] = match.group("agg")
                        continue
                if ip is None:
                    match = self.rx_ip.match(l)
                    if match:
                        ip = match.group("ip")
            # Add subinterfaces
            if ip:
                iface["subinterfaces"] += [{
                    "name": name,
                    "description": iface.get("description"),
                    "mac": iface.get("mac"),
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip]
                }]
            if name in sw:
                si = {
                    "name": name,
                    "description": iface.get("description"),
                    "mac": iface.get("mac"),
                    "enabled_afi": ["BRIDGE"],
                }
                untagged, tagged = sw[name]
                if untagged:
                    si["untagged_vlan"] = untagged
                if tagged:
                    si["tagged_vlans"] = tagged
                iface["subinterfaces"] += [si]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
