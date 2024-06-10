# ---------------------------------------------------------------------
# NAG.SNR.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Set, Dict, Any
from collections import defaultdict

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
        r"^\s*(?P<interface>\S+)\s+is\s+(?P<admin_status>up|down|administratively down)(?:\s*\(\d\))?,\s+"
        r"line protocol is\s+(?P<oper_status>up|down)"
        r"(,(?: dev)? index is (?P<snmp_ifindex>\d+))?\s*\n"
        r"(?P<other>(?:^\s+.+\n)+?)"
        r"(?:^\s+Encapsulation |^\s+Output packets statistics:)",
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
        r"(,\s+address is (?P<mac>\S+))?\s*\n",
        re.MULTILINE,
    )
    rx_alias = re.compile(r"\s+alias name is (?P<alias>.+),", re.MULTILINE)
    rx_index = re.compile(r", index is (?P<ifindex>\d+)")
    rx_alias_and_index = re.compile(r" alias name is (?P<alias>.+), index is (?P<ifindex>\d+)")
    rx_mtu = re.compile(r"MTU (?P<mtu>\d+) bytes")
    rx_pvid = re.compile(r"PVID is (?P<pvid>\d+)")
    rx_ip = re.compile(
        r"^\s+IPv4 address is:\s*\n" r"^\s+(?P<ip>\S+)\s+(?P<mask>\S+)", re.MULTILINE
    )
    rx_vlan = re.compile(
        r"^(?P<ifname>Ethernet\S+)\s*\n"
        r"^Type.+\s*\n"
        r"^Mode\s*:\s*(?P<mode>\S+)\s*\n"
        r"^Port VID\s*:\s*(?P<untagged_vlan>\d+)\s*\n"
        r"(^Trunk allowed Vlan\s*:\s*(?P<tagged_vlans>\S+)\s*\n)?",
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
        if self.is_foxgate_cli:
            return {}
        # New CLI syntax
        result = defaultdict(lambda: {"untagged": None, "tagged": []})
        v = self.cli("show switchport interface")
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

    def get_interfaces_foxgatecli(self):
        """
        For FoxGate Like CLI syntax
        :return:
        """
        v = self.cli("show interface", cached=True)
        interfaces = {}
        for match in self.rx_sh_int_old.finditer(v):
            ifname = match.group("interface")
            sub = {
                "name": match.group("interface"),
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "mac": match.group("mac"),
                "enabled_afi": ["BRIDGE"],
            }
            if match.group("mode") == "access":
                sub["untagged_vlan"] = match.group("untagged")
            else:
                sub["untagged_vlan"] = match.group("pvid")
                sub["tagged_vlans"] = self.expand_rangelist(match.group("tagged"))
            interfaces[ifname] = {
                "name": ifname,
                "type": "physical",
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "mac": match.group("mac"),
                "subinterfaces": [sub],
            }

        v = self.cli("show ip", cached=True)
        match = self.rx_mgmt.search(v)
        ip_address = f'{match.group("ip")}/{IPv4.netmask_to_len(match.group("mask"))}'
        interfaces["system"] = {
            "name": "system",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "mac": match.group("mac"),
            "subinterfaces": [
                {
                    "name": "system",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": match.group("mac"),
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": match.group("vlan_id"),
                }
            ],
        }
        return [{"interfaces": list(interfaces.values())}]

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
            if ifname.startswith("Vlan"):
                sub["vlan_ids"] = [int(ifname[4:])]
            # IP Address
            match1 = self.rx_ip.search(other)
            if match1 and "NULL" not in match1.group("ip"):
                ip_address = f'{match1.group("ip")}/{IPv4.netmask_to_len(match1.group("mask"))}'
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
            if match1 and match1.group("alias") != "(null),":
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
