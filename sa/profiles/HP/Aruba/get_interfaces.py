# ---------------------------------------------------------------------
# HP.Aruba.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import ranges_to_list


class Script(BaseScript):
    name = "HP.Aruba.get_interfaces"
    interface = IGetInterfaces

    rx_interface_splitter = re.compile(
        r"(Aggregate|Interface)\s+(?P<name>\S+) is (?P<oper>up|down)\s*(\(Administratively (?P<admin>up|down)\))?",
        re.MULTILINE,
    )
    rx_mac = re.compile(r"MAC Address: (?P<mac>\S+)")
    rx_description = re.compile(r"Description:\s*(?P<description>.+)?")
    rx_mtu = re.compile(r"MTU\s+(?P<mtu>\d+)")
    rx_aggregated = re.compile(r"Aggregated-interfaces\s+:\s+(?P<port>\S+)")
    rx_access_vlan = re.compile(r"Access VLAN:\s+(?P<access_vlan>\d+)")
    rx_native_vlan = re.compile(r"Native VLAN:\s+(?P<native_vlan>\d+)")
    rx_allowed_vlan = re.compile(r"Allowed VLAN List:\s+(?P<allowed_vlan>\S+)")
    # native-untagged,access
    rx_vlan_mode = re.compile(r"VLAN Mode:\s+(?P<vlan_mode>\S+)")
    # IPv4 ifaces
    rx_ipv4_address = re.compile(r"IPv4 address\s+(?P<ip_address>\S+)")
    #
    rx_vlans = re.compile(r"^(?P<vlan>\d+)\s+", re.MULTILINE)

    def get_vlans(self) -> List[int]:
        v = self.cli("show vlan", cached=True)
        return [int(x) for x in self.rx_vlans.findall(v)]

    def execute_cli(self, **kwargs):
        """
         Admin state is up
        Link state: up for 16 days (since Tue Nov 14 13:25:42 MSK 2023)
        Link transitions: 5
        Description: -Access Switch-
        Persona:
        Hardware: Ethernet, MAC Address: d4:e0:53:da:15:34
        MTU 9198

        """
        # Get portchannels
        all_vlans = self.get_vlans()
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        ifaces = {}
        v = self.cli("show interface")
        for ll in v.split("\n\n"):
            match = self.rx_interface_splitter.search(ll)
            if not match:
                continue
            r = {}
            for rx in [
                self.rx_mac,
                self.rx_mtu,
                self.rx_access_vlan,
                self.rx_native_vlan,
                self.rx_allowed_vlan,
                self.rx_vlan_mode,
                self.rx_ipv4_address,
            ]:
                m = rx.search(ll)
                if m:
                    r.update(m.groupdict())
            ifname = self.profile.convert_interface_name(match.group("name"))
            iftype = self.profile.get_interface_type(ifname)
            subiface = {
                "name": ifname,
                "admin_status": match.group("admin"),
                "oper_status": match.group("oper") == "up",
                "enabled_afi": [],
                # "mac": mac,
                # "snmp_ifindex": self.scripts.get_ifindex(interface=name)
            }
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": not match.group("admin"),
                "oper_status": match.group("oper") == "up",
                "mac": r.get("mac"),
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            d_match = self.rx_description.search(ll)
            if d_match and not d_match.group("description").startswith("Hardware"):
                iface["description"] = d_match.group("description")
            if "mtu" in r:
                iface["mtu"] = r["mtu"]
            if r.get("vlan_mode") == "access" and "access_vlan" in r:
                subiface["untagged_vlan"] = r["access_vlan"]
                subiface["enabled_afi"] += ["BRIDGE"]
            elif "native_vlan" in r:
                subiface["untagged_vlan"] = r["native_vlan"]
                subiface["enabled_afi"] += ["BRIDGE"]
                if "allowed_vlan" in r:
                    subiface["tagged_vlans"] = (
                        all_vlans
                        if r["allowed_vlan"] == "all"
                        else ranges_to_list(r["allowed_vlan"])
                    )
            if "ip_address" in r:
                subiface["enabled_afi"] += ["IPv4"]
                subiface["ipv4_addresses"] = [r["ip_address"]]
                if ifname.startswith("vlan"):
                    subiface["vlan_ids"] = [int(ifname[4:])]
            if iftype == "physical" and ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                iface["subinterfaces"] = []
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            iface["subinterfaces"] += [subiface]
            ifaces[ifname] = iface
        return [{"interfaces": list(ifaces.values())}]
