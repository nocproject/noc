# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    """
    @todo: STP, CTP, GVRP, LLDP, UDLD
    @todo: IGMP
    @todo: IPv6
    """
    name = "Qtech.QSW8200.get_interfaces"
    interface = IGetInterfaces

    rx_interface = re.compile(
        r"^\s+(?P<ifname>\S+) is (?P<oper_status>UP|DOWN), "
        r"administrative status is (?P<admin_status>UP|DOWN)",
        re.MULTILINE)
    rx_descr = re.compile(r"^\s+Description is (?P<descr>.+),", re.MULTILINE)
    rx_hw_mac = re.compile(
        r"^\s+Hardware is (?P<iftype>\S+), MAC address is (?P<mac>\S+)",
        re.MULTILINE)
    rx_ipv4 = re.compile(
        r"^\s+Internet Address is (?P<ipv4>\S+)", re.MULTILINE)
    rx_ipv6 = re.compile(
        r"^\s+Internet v6 Address is (?P<ipv6>\S+)", re.MULTILINE)
    # rx_jumbo = re.compile("^\s+JUMBOFRAME (?P<mtu>\d+) bytes")
    rx_mtu = re.compile("^\s+MTU (?P<mtu>\d+) bytes", re.MULTILINE)
    rx_vlan_id = re.compile("^vlan(?P<vlan_id>\d+)", re.MULTILINE)
    rx_ifname = re.compile(
        "^(?P<ifname>tengigabitethernet|gigaethernet)(?P<ifnum>\d+/\d+/\d+)",
        re.MULTILINE
    )
    rx_switch = re.compile(
        r"^Interface:.*\n"
        r"^Switch Mode:.*\n"
        r"^Reject frame type:.*\n"
        r"^Administrative Mode:.*\n"
        r"^Operational Mode: (?P<oper_mode>\S+)\s*\n"
        r"^Access Mode VLAN: (?P<a_vlan>\d+)\s*\n"
        r"^Administrative Access Egress VLANs:.*\n"
        r"^Operational Access Egress VLANs:.*\n"
        r"^Trunk Native Mode VLAN:(?P<t_vlan>.*)\n"
        r"^Trunk Native VLAN:.*\n"
        r"^Administrative Trunk Allowed VLANs:.*\n"
        r"^Operational Trunk Allowed VLANs:(?P<t_vlans>.*)\n"
        r"^Administrative Trunk Untagged VLANs:(?P<t_uvlan>.*)\n"
        r"^Operational Trunk Untagged VLANs:.*\n",
        re.MULTILINE
    )

    IFTYPES = {
        "fastethernet": "physical",
        "gigaethernet": "physical",
        "tengigabitethernet": "physical",
        "trunk": "aggregated",
        "vlan-interface": "SVI",
        "unknown": "unknown"
    }

    def execute(self):
        r = []
        for l in self.cli("show interface").split("\n\n"):
            match = self.rx_interface.search(l)
            if not match:
                continue
            ifname = match.group("ifname")
            iface = {
                "name": ifname,
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP"
            }
            sub = {
                "name": ifname,
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
                "enabled_afi": []
            }
            match = self.rx_hw_mac.search(l)
            if ifname.startswith("loopback"):
                iface["type"] = "loopback"
            elif ifname.startswith("NULL"):
                iface["type"] = "null"
            else:
                iface["type"] = self.IFTYPES[match.group("iftype")]
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if iface["type"] == "physical":
                sub["enabled_afi"] += ["BRIDGE"]
            if iface["type"] == "SVI":
                match = self.rx_vlan_id.search(ifname)
                if match:
                    sub["vlan_ids"] = [match.group("vlan_id")]
            match = self.rx_descr.search(l)
            if match:
                iface["description"] = match.group("descr")
                sub["description"] = match.group("descr")
            match = self.rx_mtu.search(l)
            if match:
                iface["mtu"] = match.group("mtu")
                sub["mtu"] = match.group("mtu")
            for match in self.rx_ipv4.finditer(l):
                if "IPv4" not in sub["enabled_afi"]:
                    sub["enabled_afi"] += ["IPv4"]
                if "ipv4_addresses" not in sub:
                    sub["ipv4_addresses"] = []
                sub["ipv4_addresses"] += [match.group("ipv4")]
            for match in self.rx_ipv6.finditer(l):
                if "IPv6" not in sub["enabled_afi"]:
                    sub["enabled_afi"] += ["IPv6"]
                if "ipv6_addresses" not in sub:
                    sub["ipv6_addresses"] = []
                sub["ipv6_addresses"] += [match.group("ipv6")]
            iface["subinterfaces"] = [sub]
            r += [iface]
        p = self.scripts.get_portchannel()
        for i in r:
            match = self.rx_ifname.search(i["name"])
            if match:
                c = self.cli(
                    "show switchport interface %s %s" %
                    (match.group("ifname"), match.group("ifnum"))
                )
                match = self.rx_switch.search(c)
                mode = match.group("oper_mode")
                if mode == "access":
                    i["subinterfaces"][0]["untagged_vlan"] = \
                        match.group("a_vlan")
                if mode == "trunk":
                    if match.group("t_uvlan").strip():
                        untagged = int(match.group("t_uvlan").strip())
                        i["subinterfaces"][0]["untagged_vlan"] = untagged
                    else:
                        untagged = 0
                    if match.group("t_vlans").strip():
                        tagged = self.expand_rangelist(
                            match.group("t_vlans").strip()
                        )
                        if untagged and (untagged in tagged):
                            tagged.remove(untagged)
                        i["subinterfaces"][0]["tagged_vlans"] = tagged
            for pc in p:
                if i["name"] in pc["members"]:
                    i["aggregated_interface"] = pc["interface"]
                    if pc["type"] == "L":
                        i["enabled_protocols"] = ["LACP"]
        return [{"interfaces": r}]
