# ----------------------------------------------------------------------
# 3Com.4500.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "3Com.4500.get_interfaces"
    interface = IGetInterfaces

    rx_sh_svi = re.compile(
        r"^\s*(?P<interface>\S+) current state : ?(?P<admin_status>(UP|DOWN|ADMINISTRATIVELY DOWN))\s*.IP Sending Frames' Format is \S+, Hardware address is (?P<mac>\S+).Description: (?P<description>(\S+ \S+ \S+ \S+|\S+ \S+ \S+|\S+ \S+|\S+)).Line protocol current state :(?P<oper_status>\S+).Internet Address is (?P<ip>\S+)\/(?P<mask>\d+)( Primary|, acquired via DHCP).The Maximum Transmit Unit is \d+",
        re.DOTALL | re.MULTILINE,
    )
    rx_iface = re.compile(
        r"^\s*(?P<iface>((\S+|)Ethernet|\S+Aggregation)\S+) current state :\s+(?P<status>(UP|DOWN|ADMINISTRATIVELY DOWN))\s*$"
    )
    rx_mac = re.compile(r"^\s*IP Sending Frames' Format is \S+, Hardware address is (?P<mac>\S+)$")
    rx_description = re.compile(r"^\s*Description:\s+(?P<description>.+)$")
    rx_type = re.compile(r"^\s*Port link-type: (?P<type>\S+)$")
    rx_tagged = re.compile(r"^\s*VLAN passing  : (?P<tagged>.+)$")
    rx_tag = re.compile(r"^\s*Tagged\s+VLAN ID :\s+(?P<tagged>.+)$")
    rx_untag = re.compile(r"^\s*Untagged\s+VLAN ID :\s+(?P<untagged>.+)$")

    types = {
        "Et": "physical",  # Ethernet
        "Gi": "physical",  # GigabitEthernet
        "Po": "aggregated",  # Aggregated
    }

    def get_ospfint(self):
        return []

    def get_ripint(self):
        return []

    def execute(self):
        interfaces = []
        mac = ""
        # Get portchannels
        portchannel_members = {}
        # portchannel = self.scripts.get_portchannel()
        # portchannel = self.scripts.my_get_portchannel()
        # portchannel = []
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        # Get L3 interfaces

        # TODO Get router interfaces
        # ospfs = self.get_ospfint()
        # rips = self.get_ripint()

        ifaces = self.cli("display interface").strip(" ")
        for match in self.rx_sh_svi.finditer(ifaces):
            description = match.group("description")
            if not description:
                description = ""
            ifname = match.group("interface")
            ip = match.group("ip")
            netmask = match.group("mask")
            enabled_afi = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                ip_ver = "is_ipv6"
                enabled_afi += ["IPv6"]
                ip = ip + "/" + netmask
                ip_list = [ip]
            else:
                ip_interfaces = "ipv4_addresses"
                ip_ver = "is_ipv4"
                enabled_afi += ["IPv4"]
                ip = ip + "/" + netmask
                ip_list = [ip]
            vlan = ifname[14:]
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            mac = match.group("mac")
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": a_stat,
                "oper_status": o_stat,
                "mac": mac,
                "description": description,
                "subinterfaces": [
                    {
                        "name": ifname,
                        "description": description,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        ip_ver: True,
                        "enabled_afi": enabled_afi,
                        ip_interfaces: ip_list,
                        "mac": mac,
                        "vlan_ids": self.expand_rangelist(vlan),
                    }
                ],
            }
            interfaces += [iface]

        # Get L2 interfaces
        ifaces = ifaces.splitlines()
        for i in range(len(ifaces)):
            match = self.rx_iface.search(ifaces[i])
            if match:
                ifname = match.group("iface")
                if ifname[:18] == "Bridge-Aggregation":
                    ifname = "Po " + ifname.split("Bridge-Aggregation")[1]
                else:
                    ifname = ifname.replace("Ethernet", "Et ")
                    # ifname = ifname.replace('GigabitEthernet', 'Gi ')
                o_stat = match.group("status") == "UP"
                a_stat = match.group("status") != "ADMINISTRATIVELY DOWN"

                i += 1
                match = self.rx_mac.search(ifaces[i])
                if match:
                    mac = match.group("mac")
                i += 1
                match = self.rx_description.search(ifaces[i])
                if match:
                    description = match.group("description")
                else:
                    description = ""
                iface = {
                    "name": ifname,
                    "type": self.types[ifname[:2]],
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "mac": mac,
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": a_stat,
                            "oper_status": o_stat,
                            "mac": mac,
                            # "snmp_ifindex": self.scripts.get_ifindex(interface=ifname)
                            # "snmp_ifindex": ifname.split('/')[2]
                        }
                    ],
                }

                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    if is_lacp:
                        iface["enabled_protocols"] = ["LACP"]
                else:
                    iface["description"] = description
                    iface["subinterfaces"][0]["description"] = description
                    iface["subinterfaces"][0]["is_bridge"] = True
                    iface["subinterfaces"][0]["enabled_afi"] = ["BRIDGE"]
                    while not self.rx_type.search(ifaces[i]):
                        i += 1
                    match = self.rx_type.search(ifaces[i])
                    vtype = match.group("type")
                    i += 1
                    if vtype == "trunk":
                        match = self.rx_tagged.search(ifaces[i])
                        tagged = match.group("tagged")
                        tagged = tagged.replace("(default vlan)", "")
                        tagged_ = []
                        for j in self.expand_rangelist(tagged):
                            tagged_.append(int(j))
                        iface["subinterfaces"][0]["tagged_vlans"] = tagged_
                    else:
                        match = self.rx_tag.search(ifaces[i])
                        tagged = match.group("tagged")
                        # try:
                        if "none" not in tagged:
                            iface["subinterfaces"][0]["tagged_vlans"] = self.expand_rangelist(
                                tagged
                            )
                        continue
                interfaces += [iface]

        return [{"interfaces": interfaces}]
