# ---------------------------------------------------------------------
# NAG.SNR.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
    rx_alias = re.compile(r"\s+alias name is (?P<alias>\S+)\s", re.MULTILINE)
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

    def execute_cli(self):
        interfaces = []
        # Get LLDP interfaces
        lldp = []
        c = self.cli("show lldp", ignore_errors=True)
        if self.rx_lldp_en.search(c):
            ll = self.rx_lldp.search(c)
            if ll:
                lldp = ll.group("local_if").split()
        v = self.cli("show interface", cached=True)
        for match in self.rx_sh_int.finditer(v):
            name = match.group("interface")
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            other = match.group("other")
            match1 = self.rx_hw.search(other)
            iface = {
                "type": self.profile.get_interface_type(name),
                "name": name,
                "admin_status": a_stat,
                "oper_status": o_stat,
            }
            sub = {"name": name, "admin_status": a_stat, "oper_status": o_stat}
            # LLDP protocol
            if name in lldp:
                iface["enabled_protocols"] = ["LLDP"]
            if iface["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
            if match1.group("mac"):
                iface["mac"] = match1.group("mac")
                sub["mac"] = match1.group("mac")
            match1 = self.rx_alias.search(other)
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
            # Correct alias and index on some device
            match1 = self.rx_alias_and_index.search(other)
            if match1:
                if match1.group("alias") != "(null)":
                    iface["description"] = match1.group("alias")
                    sub["description"] = match1.group("alias")
                iface["snmp_ifindex"] = match1.group("ifindex")
                sub["snmp_ifindex"] = match1.group("ifindex")
            match1 = self.rx_mtu.search(other)
            if match1:
                sub["mtu"] = match1.group("mtu")
            match1 = self.rx_pvid.search(other)
            if match1:
                sub["untagged_vlan"] = match1.group("pvid")
            if name.startswith("Vlan"):
                sub["vlan_ids"] = [int(name[4:])]
            match1 = self.rx_lag_port.search(other)
            if match1:
                iface["aggregated_interface"] = match1.group("lag_port")
            match1 = self.rx_ip.search(other)
            if match1:
                if "NULL" in match1.group("ip"):
                    continue
                ip_address = "%s/%s" % (
                    match1.group("ip"),
                    IPv4.netmask_to_len(match1.group("mask")),
                )
                sub["ipv4_addresses"] = [ip_address]
                sub["enabled_afi"] = ["IPv4"]
            iface["subinterfaces"] = [sub]
            interfaces += [iface]
        if interfaces:
            # New CLI syntax
            v = self.cli("show switchport interface")
            for match in self.rx_vlan.finditer(v):
                ifname = match.group("ifname")
                untagged_vlan = match.group("untagged_vlan")
                for i in interfaces:
                    if ifname == i["name"]:
                        i["subinterfaces"][0]["untagged_vlan"] = untagged_vlan
                        if match.group("tagged_vlans"):
                            tagged_vlans = match.group("tagged_vlans").replace(";", ",")
                            i["subinterfaces"][0]["tagged_vlans"] = self.expand_rangelist(
                                tagged_vlans
                            )
                        break
        else:
            # Old CLI syntax. V6.5.1.21 and older
            for match in self.rx_sh_int_old.finditer(v):
                iface = {
                    "name": match.group("interface"),
                    "type": "physical",
                    "admin_status": match.group("admin_status") == "enabled",
                    "oper_status": match.group("oper_status") == "up",
                    "mac": match.group("mac"),
                }
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
                iface["subinterfaces"] = [sub]
                interfaces += [iface]
            v = self.cli("show ip", cached=True)
            match = self.rx_mgmt.search(v)
            ip_address = "%s/%s" % (
                match.group("ip"),
                IPv4.netmask_to_len(match.group("mask")),
            )
            iface = {
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
            interfaces += [iface]
        return [{"interfaces": interfaces}]
