# ---------------------------------------------------------------------
# HP.Aruba.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "HP.Aruba.get_interfaces"
    interface = IGetInterfaces

    rx_interface_splitter = re.compile(
        r"Interface\s+(?P<name>\S+) is (?P<oper>up|down)\s*(\(Administratively (?P<admin>up|down)\))?",
        re.MULTILINE,
    )
    rx_mac = re.compile(r"MAC Address: (?P<mac>\S+)")
    rx_description = re.compile(r"Description:\s+(?P<description>.+)\s*")
    rx_mtu = re.compile(r"MTU\s+(?P<mtu>\d+)")
    rx_aggregated = re.compile(r"Aggregated-interfaces\s+:\s+(?P<port>\S+)")

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
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        ifaces = {}
        v = self.cli("show interface")
        prev = None
        for match in self.rx_interface_splitter.finditer(v):
            if not prev:
                prev = match
                continue
            ll = v[prev.end() : match.start()]
            r = {}
            for rx in [self.rx_mac, self.rx_description, self.rx_mtu]:
                m = rx.search(ll)
                if m:
                    r.update(m.groupdict())
            ifname = prev.group("name")
            iftype = self.profile.get_interface_type(ifname)
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": not prev.group("admin"),
                "oper_status": prev.group("oper") == "up",
                "mac": r.get("mac"),
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": prev.group("admin"),
                        "oper_status": prev.group("oper") == "up",
                        "enabled_afi": [],
                        # "mac": mac,
                        # "snmp_ifindex": self.scripts.get_ifindex(interface=name)
                    }
                ],
            }
            if iftype == "physical" and ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                iface["subinterfaces"] = []
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            ifaces[ifname] = iface
            prev = match
        return [{"interfaces": list(ifaces.values())}]
