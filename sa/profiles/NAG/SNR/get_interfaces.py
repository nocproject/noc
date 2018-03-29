# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NAG.SNR.get_interfaces
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


class Script(BaseScript):
    name = "NAG.SNR.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_lldp_en = re.compile(r"LLDP has been enabled globally?")
    rx_lldp = re.compile(r"LLDP enabled port : (?P<local_if>\S*.+)$", re.MULTILINE)
    rx_sh_int = re.compile(
        r"^\s*(?P<interface>\S+)\s+is\s+(?P<admin_status>up|down),\s+"
        r"line protocol is\s+(?P<oper_status>up|down)"
        r"(, dev index is (?P<snmp_ifindex>\d+))?\s*\n"
        r"^\s+(?P<ifname>[^\n]+)"
        r"(?P<other>.+?)\n"
        r"^\s+Encapsulation ",
        re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    rx_hw = re.compile(
        r"^\s+Hardware is (?P<hw_type>\S+)(, active is \S+)?"
        r"(, address is (?P<mac>\S+))?\s*\n",
        re.MULTILINE
    )
    rx_alias = re.compile(
        r"\s+alias name is (?P<alias>\S+)\s",
        re.MULTILINE | re.IGNORECASE)
    rx_index = re.compile(r", index is (?P<ifindex>\d+)")
    rx_mtu = re.compile(r"MTU (?P<mtu>\d+) bytes")
    rx_pvid = re.compile(r"PVID is (?P<pvid>\d+)")
    rx_ip = re.compile(
        r"^\s+IPv4 address is:\s*\n"
        r"^\s+(?P<ip>\S+)\s+(?P<mask>\S+)",
        re.MULTILINE
    )
    rx_vlan = re.compile(
        r"^(?P<ifname>Ethernet\S+)\s*\n"
        r"^Type.+\s*\n"
        r"^Mode\s*:\s*(?P<mode>\S+)\s*\n"
        r"^Port VID\s*:\s*(?P<untagged_vlan>\d+)\s*\n"
        r"(^Trunk allowed Vlan\s*:\s*(?P<tagged_vlans>\S+)\s*\n)?",
        re.MULTILINE
    )

    HW_TYPES = {
        "Fast-Ethernet": "physical",
        "Gigabit-Combo": "physical",
        "Gigabit-TX": "physical",
        "SFP": "physical",
        "EtherChannel": "aggregated",
        "EtherSVI": "SVI"
    }

    def execute(self):
        interfaces = []
        # Get LLDP interfaces
        lldp = []
        c = self.cli("show lldp", ignore_errors=True)
        if self.rx_lldp_en.search(c):
            ll = self.rx_lldp.search(c)
            lldp = ll.group("local_if").split()
        v = self.cli("show interface", cached=True)
        for match in self.rx_sh_int.finditer(v):
            name = match.group("interface")
            ifname = match.group("ifname")
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            other = match.group("other")
            match1 = self.rx_hw.search(other)
            iface = {
                "type": self.HW_TYPES[match1.group("hw_type")],
                "name": name,
                "admin_status": a_stat,
                "oper_status": o_stat
            }
            sub = {
                "name": name,
                "admin_status": a_stat,
                "oper_status": o_stat
            }
            # LLDP protocol
            if name in lldp:
                iface["enabled_protocols"] = ["LLDP"]
            if iface["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
            if match1.group("mac"):
                iface["mac"] = match1.group("mac")
                sub["mac"] = match1.group("mac")
            match1 = self.rx_alias.search(ifname)
            if match1 and match1.group("alias") != "(null),":
                iface["description"] = match1.group("alias")
                sub["description"] = match1.group("alias")
            match1 = self.rx_index.search(other)
            if match1:
                iface["snmp_ifindex"] = match1.group("ifindex")
                sub["snmp_ifindex"] = match1.group("ifindex")
            else:
                if match.group("snmp_ifindex"):
                    iface["snmp_ifindex"] = match.group("snmp_ifindex")
                    sub["snmp_ifindex"] = match.group("snmp_ifindex")
            match1 = self.rx_mtu.search(other)
            if match1:
                sub["mtu"] = match1.group("mtu")
            match1 = self.rx_pvid.search(other)
            if match1:
                sub["untagged_vlan"] = match1.group("pvid")
            if name.startswith("Vlan"):
                sub["vlan_ids"] = [int(name[4:])]
            match1 = self.rx_ip.search(other)
            if match1:
                if "NULL" in match1.group("ip"):
                    continue
                ip_address = "%s/%s" % (
                    match1.group("ip"),
                    IPv4.netmask_to_len(match1.group("mask"))
                )
                sub["ipv4_addresses"] = [ip_address]
                sub["enabled_afi"] = ["IPv4"]
            iface["subinterfaces"] = [sub]
            interfaces += [iface]
        v = self.cli("show switchport interface")
        for match in self.rx_vlan.finditer(v):
            ifname = match.group("ifname")
            untagged_vlan = match.group("untagged_vlan")
            for i in interfaces:
                if ifname == i["name"]:
                    i["subinterfaces"][0]["untagged_vlan"] = untagged_vlan
                    if match.group("tagged_vlans"):
                        tagged_vlans = match.group("tagged_vlans").replace(
                            ";", ","
                        )
                        i["subinterfaces"][0]["tagged_vlans"] = \
                            self.expand_rangelist(tagged_vlans)
                    break
        return [{"interfaces": interfaces}]
