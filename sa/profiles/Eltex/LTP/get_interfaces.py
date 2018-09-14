# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.LTP.get_interfaces"
    interface = IGetInterfaces

    rx_mgmt = re.compile(
        r"^\s+Ipaddr:\s+(?P<ip>\S+)\s*\n"
        r"^\s+Netmask:\s+(?P<mask>\S+)\s*\n"
        r"^\s+Vlan management:\s+(?P<vlan_id>\d+)\s*\n",
        re.MULTILINE
    )
    rx_mac = re.compile(r"^\s+MAC address: (?P<mac>\S+)", re.MULTILINE)
    rx_status = re.compile(r"^.+\d\s+(?P<oper_status>up|down|off)", re.MULTILINE)

    def normalize_ifname(self, port):
        port = port.strip()
        while port.find("  ") != -1:
            port = port.replace("  ", " ")
        while port.find("- ") != -1:
            port = port.replace("- ", "-")
        return port

    def create_iface(self, i, iftype):
        ifname = " ".join(i[0].split())
        if not ifname.startswith(iftype):
            return None
        pvid = i[1]
        if i[4] not in ["none", "N/S"]:
            tagged = self.expand_rangelist(i[4])
        else:
            tagged = []
        untagged = i[5]
        if untagged in ["none", "N/S"]:
            untagged = pvid
        iface = {
            "name": ifname,
            "type": "physical",
            "subinterfaces": [{
                "name": ifname,
                "enabled_afi": ["BRIDGE"]
            }]
        }
        if untagged != "N/S":
            iface["subinterfaces"][0]["untagged_vlan"] = int(untagged)
        if tagged:
            iface["subinterfaces"][0]["tagged_vlans"] = tagged
        return iface

    def execute(self):
        interfaces = []

        with self.profile.switch(self):
            c = self.cli("show vlan")
            t = parse_table(c, allow_wrap=True, footer="dummy footer")
            for i in t:
                vlan_id = i[0]
                if i[2] != "none":
                    tagged = i[2].split(", ")
                    for port in tagged:
                        ifname = self.normalize_ifname(port)
                        found = False
                        for iface in interfaces:
                            if iface["name"] == ifname:
                                if "tagged_vlans" in iface["subinterfaces"][0]:
                                    iface["subinterfaces"][0][
                                        "tagged_vlans"
                                    ] += [vlan_id]
                                else:
                                    iface["subinterfaces"][0][
                                        "tagged_vlans"
                                    ] = [vlan_id]
                                found = True
                                break
                        if not found:
                            iface = {
                                "name": ifname,
                                "type": "physical",
                                "subinterfaces": [{
                                    "name": ifname,
                                    "enabled_afi": ["BRIDGE"],
                                    "tagged_vlans": [vlan_id]
                                }]
                            }
                            interfaces += [iface]
                if i[3] != "none":
                    untagged = i[3].split(", ")
                    for port in untagged:
                        ifname = self.normalize_ifname(port)
                        found = False
                        for iface in interfaces:
                            if iface["name"] == ifname:
                                iface["subinterfaces"][0][
                                    "untagged_vlan"
                                ] = vlan_id
                                found = True
                                break
                        if not found:
                            iface = {
                                "name": ifname,
                                "type": "physical",
                                "subinterfaces": [{
                                    "name": ifname,
                                    "enabled_afi": ["BRIDGE"],
                                    "untagged_vlan": vlan_id
                                }]
                            }
                            interfaces += [iface]
            for i in interfaces:
                c = self.cli("show interfaces mac-address %s" % i["name"])
                match = self.rx_mac.search(c)
                if match:
                    i["mac"] = match.group("mac")
                    i["subinterfaces"][0]["mac"] = match.group("mac")
                try:
                    c = self.cli("show interfaces status %s" % i["name"])
                    match = self.rx_status.search(c)
                    i["oper_status"] = match.group("oper_status") == "up"
                    i["subinterfaces"][0]["oper_status"] = match.group("oper_status") == "up"
                    i["admin_status"] = match.group("oper_status") != "off"
                    i["subinterfaces"][0]["admin_status"] = match.group("oper_status") != "off"
                except self.CLISyntaxError:
                    pass
        c = self.cli("show management")
        match = self.rx_mgmt.search(c)
        ip_address = "%s/%s" % (
            match.group("ip"), IPv4.netmask_to_len(match.group("mask"))
        )
        iface = {
            "name": "management",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "subinterfaces": [{
                "name": "management",
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
                "vlan_ids": int(match.group("vlan_id"))
            }]
        }
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        iface["mac"] = mac
        iface["subinterfaces"][0]["mac"] = mac
        interfaces += [iface]
        return [{"interfaces": interfaces}]
