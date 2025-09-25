# ---------------------------------------------------------------------
# Eltex.MES5448.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^Port: (?P<ifname>\S+)\s*\n"
        r"^VLAN Membership Mode: (?P<mode>\S+)\s*\n"
        r"^Access Mode VLAN: (?P<access_vlan>\d+).*\n"
        r"^General Mode PVID:.+\n"
        r"^General Mode Ingress Filtering:.+\n"
        r"^General Mode Acceptable Frame Type:.+\n"
        r"^General Mode Dynamically Added VLANs:\s*\n"
        r"^General Mode Untagged VLANs: (?P<guntagged_vlan>\d+).*\n"
        r"^General Mode Tagged VLANs:(?P<gtagged_vlans>.*)\n"
        r"^General Mode Forbidden VLANs:\s*\n"
        r"^Trunking Mode Native VLAN: (?P<untagged_vlan>\d+).*\n"
        r"^Trunking Mode Native VLAN tagging: .+\n"
        r"^Trunking Mode VLANs Enabled:(?P<tagged_vlans>.*)\n"
        r"^Protected Port:.*\n",
        re.MULTILINE,
    )
    rx_ifdescr = re.compile(
        r"^Interface....... (?P<ifname>\S+)\s*\n"
        r"^ifIndex\.+ (?P<snmp_ifindex>\d+)\s*\n"
        r"^Description\.+.*\s*\n"
        r"^MAC address\.+(?P<mac>.*)\n",
        re.MULTILINE,
    )
    rx_mac = re.compile(r"MAC Address used by Routing VLANs:\s+(?P<mac>\S+)")

    def execute(self):
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        # Get list of aggreged  interfaces
        aggregated = []
        for i in parse_table(self.cli("show port-channel all"), allow_wrap=True):
            aggregated += [i[0]]

        # Get LLDP interfaces
        lldp = []
        for i in parse_table(self.cli("show lldp interface all")):
            if i[2] == "Enabled" or i[3] == "Enabled":
                lldp += [i[0]]

        # Get GVRP interfaces
        gvrp = []
        for i in parse_table(self.cli("show gvrp configuration all")):
            if i[4] == "Enabled":
                gvrp += [i[0]]

        # Get STP interfaces
        stp = []
        for i in parse_table(self.cli("show spanning-tree active")):
            if i[1] == "Enabled":
                stp += [i[0]]

        # Get OSPF interfaces
        ospf = []
        for i in parse_table(self.cli("show ip ospf interface brief")):
            if i[1] == "Enabled":
                ospf += [i[0]]

        interfaces = []
        # Get ifname and description
        for i in parse_table(self.cli("show interfaces status all"), allow_wrap=True):
            ifname = i[0]
            iface = {
                "name": ifname,
                "type": "physical",
                "enabled_protocols": [],
                "subinterfaces": [
                    {"name": ifname, "enabled_afi": ["BRIDGE"], "enabled_protocols": []}
                ],
            }
            if i[1]:
                iface["description"] = i[1]
                iface["subinterfaces"][0]["description"] = i[1]
            # aggregated interface
            if ifname in aggregated:
                iface["type"] = "aggregated"
            # LLDP protocol
            if ifname in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            # GVRP protocol
            if ifname in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            # STP protocol
            if ifname in stp:
                iface["enabled_protocols"] += ["STP"]
            # OSPF protocol
            if ifname in ospf:
                iface["subinterfaces"][0]["enabled_protocols"] += ["OSPF"]
            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            c = self.cli("show port description %s" % ifname)
            match = self.rx_ifdescr.search(c)
            if match:
                iface["snmp_ifindex"] = match.group("snmp_ifindex")
                mac = match.group("mac").strip()
                if mac:
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
            interfaces += [iface]
        c = self.cli("show interfaces switchport")
        for match in self.rx_port.finditer(c):
            ifname = match.group("ifname")
            mode = match.group("mode")
            if mode == "Access":
                untagged = match.group("access_vlan").strip()
                tagged = ""
            elif mode == "Trunk":
                untagged = match.group("untagged_vlan").strip()
                tagged = match.group("tagged_vlans").strip()
            elif mode == "General":
                untagged = match.group("guntagged_vlan").strip()
                tagged = match.group("gtagged_vlans").strip()
            else:
                raise self.NotSupportedError()
            if not untagged:
                untagged = 1
            if not tagged:
                tagged = []
            elif tagged == "All":
                tagged = self.expand_rangelist("1-4094")
            else:
                tagged = self.expand_rangelist(tagged)
            for i in interfaces:
                if ifname == i["name"]:
                    i["subinterfaces"][0]["untagged_vlan"] = untagged
                    i["subinterfaces"][0]["tagged_vlans"] = tagged
                    break
        c = self.cli("show ip vlan")
        match = self.rx_mac.search(c)
        mac = match.group("mac")
        for i in parse_table(c):
            for iface in interfaces:
                if i[1] == iface["name"]:
                    iface["type"] = "SVI"
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["vlan_ids"] = [i[0]]
                    iface["subinterfaces"][0]["ip_addresses"] = [
                        "%s/%s" % (i[2], IPv4.netmask_to_len(i[3]))
                    ]
                    iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                    break
        return [{"interfaces": interfaces}]
