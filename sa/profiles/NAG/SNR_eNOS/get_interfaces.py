# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Set, Dict, Any
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_lldp_en = re.compile(r"LLDP has been enabled globally?")
    rx_lldp = re.compile(r"LLDP enabled port : (?P<local_if>\S*.+)$", re.MULTILINE)
    rx_sh_int = re.compile(
        r"^\s*(?P<interface>\S+)\s+is\s+(?P<admin_status>up|down|administratively down)(?:\s*\(\d\))?,\s+"
        r"line protocol is\s+(?P<oper_status>up|down)"
        r"(^\s.*addr: (?P<hwaddr>\d+))?\s*\n"
        r"(?P<other>(?:^\s+.+\n)+?)"
        # r"(?:^\s+FlowControl |^\s+inet)",
        r"(?:^\n)",
        re.MULTILINE,
    )
    rx_sh_int_old = re.compile(
        r"^\s+(?:Fast|Gigabit) Ethernet (?P<interface>\S+) current state: (?P<admin_status>\S+), port link is (?P<oper_status>\S+)\s*\n"
        r"(?:^\s+Port type status : .+\n)?"
        r"(?:^\s+Time duration of linkup is .+\n)?"
        r"^\s+Hardware address is (?P<mac>\S+)\s*\n"
        r"^\s+SetSpeed is .+\n"
        r"^\s+Current port type: .+\n"
        r"(?:^\s+Transceiver is .+\n)?"
        r"(?:^\s+Transceiver Compliance: .+\n)?"
        r"^\s+Priority is \d+\s*\n"
        r"^\s+Flow control is .+\n"
        r"^\s+Broadcast storm control target rate is .+\n"
        r"^\s+PVID is (?P<pvid>\d+)\s*\n"
        r"^\s+Port mode: (?P<mode>trunk|access)\s*\n"
        r"(?:^\s+Untagged\s+VLAN ID: (?P<untagged>\d+)\s*\n)?"
        r"(?:^\s+Vlan\s+allowed: (?P<tagged>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_hw = re.compile(
        r"^\s+Hardware is (?P<hw_type>\S+)(\(card not installed\))?(, active is \S+)?"
        r"(\s+Current HW addr: (?P<mac>\S+))?\s*\n",
        re.MULTILINE,
    )
    rx_alias = re.compile(r"Description: (?P<alias>.+)", re.MULTILINE)
    rx_index = re.compile(r"\s+Index (?P<ifindex>\d+)")
    rx_alias_and_index = re.compile(r" alias name is (?P<alias>.+), index is (?P<ifindex>\d+)")
    rx_mtu = re.compile(r"\s+.*mtu (?P<mtu>\d+)")
    rx_pvid = re.compile(r"PVID is (?P<pvid>\d+)")
    rx_ip = re.compile(r"inet (?P<ip>\S+)/(?P<mask>\S+)", re.MULTILINE)
    rx_vlan = re.compile(
        r"^interface (?P<ifname>(?:xe|ge)\S+)\s*\n"
        r"(?:|^ spanning-tree.+\s*\n)"
        r"(?:|^ description.+\s*\n)"
        r"(?:|^ speed-duplex.+\s*\n)"
        r"^ switchport mode (?P<mode>\S+)\s*\n"
        r"(^ switchport access vlan (?P<untagged_vlan>\d+)\s*\n|^ switchport trunk allowed vlan (?P<tagged_vlans>\S+))",
        re.MULTILINE,
    )
    rx_mgmt = re.compile(
        r"^ip address\s+: (?P<ip>\S+)\s*\n"
        r"^netmask\s+: (?P<mask>\S+)\s*\n"
        r"^gateway\s+: .+\n"
        r"^ManageVLAN\s+: (?P<vlan_id>\d+)\s*\n"
        r"^MAC address\s+: (?P<mac>\S+)",
        re.MULTILINE,
    )
    rx_lag_port = re.compile(r"\s*\S+ is LAG member port, LAG port:(?P<lag_port>\S+)\n")

    def get_switchport_cli(self) -> Dict[str, Dict[str, Any]]:
        result = defaultdict(lambda: {"untagged": None, "tagged": []})
        v = self.cli("show running-config interface")
        v = v.replace("\n switchport trunk allowed vlan add ", ",")
        for match in self.rx_vlan.finditer(v):
            ifname = match.group("ifname")
            result[ifname]["untagged"] = match.group("untagged_vlan")
            if match.group("tagged_vlans"):
                tagged_vlans = match.group("tagged_vlans").replace(";", ",")
                result[ifname]["tagged"] = self.expand_rangelist(tagged_vlans)
        return result

    def get_interface_lldp(self) -> Set[str]:
        lldp = set()
        if self.is_foxgate_cli:
            return lldp
        c = self.cli("show lldp", ignore_errors=True)
        if self.rx_lldp_en.search(c):
            ll = self.rx_lldp.search(c)
            if ll:
                lldp = set(ll.group("local_if").split())
        return lldp

    def execute_cli(self, **kwargs):
        interfaces = {}
        if self.is_foxgate_cli:
            return self.get_interfaces_foxgatecli()
        # Get LLDP enabled interfaces
        lldp = self.get_interface_lldp()
        # Get switchports and fill tagged/untagged lists if they are not empty
        switchports = self.get_switchport_cli()
        v = self.cli("show interface", cached=True)
        for match in self.rx_sh_int.finditer(v):
            ifname = match.group("interface")
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_protocols": [],
                "enabled_afi": [],
            }
            # Switchport
            if ifname in switchports:
                # Bridge
                sub["enabled_afi"] += ["BRIDGE"]
                u, t = switchports[ifname]["untagged"], switchports[ifname].get("tagged")
                if u:
                    sub["untagged_vlan"] = u
                if t:
                    sub["tagged_vlans"] = t
            # Other
            other = match.group("other")
            # MTU
            match1 = self.rx_mtu.search(other)
            if match1:
                sub["mtu"] = match1.group("mtu")
            # PVID
            match1 = self.rx_pvid.search(other)
            if match1:
                sub["untagged_vlan"] = match1.group("pvid")
            if ifname.startswith("vlan"):
                sub["vlan_ids"] = [int(ifname[4:])]
            # IP Address
            match1 = self.rx_ip.search(other)
            if match1 and "NULL" not in match1.group("ip"):
                ip_address = f'{match1.group("ip")}/{match1.group("mask")}'
                sub["ipv4_addresses"] = [ip_address]
                sub["enabled_afi"] = ["IPv4"]
            iface = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "type": self.profile.get_interface_type(ifname),
                "enabled_protocols": [],
                "subinterfaces": [sub],
            }
            # MAC
            match1 = self.rx_hw.search(other)
            if match1.group("mac"):
                iface["mac"] = match1.group("mac")
                sub["mac"] = match1.group("mac")
            # Description
            match1 = self.rx_alias.search(other)
            if match1 and match1.group("alias") != "(null)":
                iface["description"] = match1.group("alias")
                sub["description"] = match1.group("alias")
            # Ifindex
            match1 = self.rx_index.search(other)
            if match1:
                iface["snmp_ifindex"] = match1.group("ifindex")
                sub["snmp_ifindex"] = match1.group("ifindex")
            elif match.group("snmp_ifindex"):
                iface["snmp_ifindex"] = match.group("snmp_ifindex")
                sub["snmp_ifindex"] = match.group("snmp_ifindex")
            # LAG
            match1 = self.rx_lag_port.search(other)
            if match1:
                iface["aggregated_interface"] = match1.group("lag_port")
            # LLDP protocol
            if ifname in lldp:
                iface["enabled_protocols"] = ["LLDP"]
            interfaces[ifname] = iface

        return [{"interfaces": list(interfaces.values())}]
