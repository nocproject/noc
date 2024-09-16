# ---------------------------------------------------------------------
# DLink.DAS.get_interfaces
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


class Script(BaseScript):
    name = "DLink.DAS.get_interfaces"
    interface = IGetInterfaces
    rx_eth = re.compile(
        r"^Interface\s+: (?P<name>\S+)\s*\n"
        r"^Type.+\n"
        r"^IP Address\s+: (?P<ip>\S+)\s+Mask\s+: (?P<mask>\S+)\s*\n"
        r"^Pkt Type.+\n"
        r"^Orl\(mbps\).+\n"
        r"^Configured Duplex.+\n"
        r"^Configured Speed.+\n"
        r"^Profile Name.+\n"
        r"^Mgmt VLAN Index\s+: (?P<vlan_id>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_stats = re.compile(
        r"^Interface\s+: (?P<name>\S+)\s+Description\s+: (?P<descr>.*)\n"
        r"^Type\s+: (?P<type>\S+)\s+Mtu\s+: (?P<mtu>\d+)\s*\n"
        r"^Bandwidth\s+: \d+\s+Phy Adddr\s+: (?P<mac>\S+)\s*\n"
        r"^Last Change\(sec\).+\n"
        r"^Admin Status\s+: (?P<admin_status>\S+)\s+Operational Status : (?P<oper_status>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_port_id = re.compile(
        r"^Port Id\s+: (?P<id>\d+)\s+IfName\s+: (?P<name>\S+)\s*\n", re.MULTILINE
    )
    rx_vlan = re.compile(
        r"^VLAN Index\s+: (?P<vlan_id>\d+)\s*\n"
        r"^VLAN Status.+\n"
        r"^Egress Ports\s+: (?P<ports>.+)\n"
        r"^Untagged Ports\s+: (?P<untagged>.+)\n",
        re.MULTILINE,
    )
    IF_TYPES = {
        "ETHERNET": "physical",
        "EOA": "unknown",
        "Adsl": "physical",
        "Interleaved": "unknown",
        "AAL5": "unknown",
        "Fast": "unknown",
        "ATM": "unknown",
    }

    def execute(self):
        interfaces = []
        v = self.cli("get interface stats")
        for match in self.rx_stats.finditer(v):
            i = {
                "name": match.group("name"),
                "type": self.IF_TYPES[match.group("type")],
                "admin_status": match.group("admin_status") == "Up",
                "oper_status": match.group("oper_status") == "Up",
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": match.group("name"),
                        "admin_status": match.group("admin_status") == "Up",
                        "oper_status": match.group("oper_status") == "Up",
                        # "ifindex": 1,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            ifindex = self.profile.get_ifindexes(match.group("name"))
            if ifindex:
                i["ifindex"] = ifindex
            if match.group("mtu") != "0":
                i["subinterfaces"][0]["mtu"] = match.group("mtu")
            if match.group("mac") != "00:00:00:00:00:00":
                i["mac"] = match.group("mac")
                i["subinterfaces"][0]["mac"] = match.group("mac")
            if match.group("descr").strip() != "":
                descr = match.group("descr").strip()
                i["description"] = descr
                i["subinterfaces"][0]["description"] = descr
            if match.group("type") == "ATM":
                i["subinterfaces"][0]["enabled_afi"] += ["ATM"]
            interfaces += [i]
        v = self.cli("get ethernet intf")
        for match in self.rx_eth.finditer(v):
            ifname = match.group("name")
            ip = match.group("ip")
            mask = match.group("mask")
            if ip == "0.0.0.0":
                continue
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            for i in interfaces:
                if i["name"] == ifname:
                    i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                    i["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
                    if match.group("vlan_id") != "-":
                        i["subinterfaces"][0]["vlan_ids"] = [match.group("vlan_id")]
                    break
        port_ids = {}
        v = self.cli("get bridge port intf")
        for match in self.rx_port_id.finditer(v):
            port_ids[match.group("id")] = match.group("name")
        v = self.cli("get vlan curr info")
        for match in self.rx_vlan.finditer(v):
            vlan_id = match.group("vlan_id")
            ports = match.group("ports").strip()
            if ports == "None":
                continue
            untagged = match.group("untagged").strip()
            bridge_ids = ports.split()
            for port_id in bridge_ids:
                if port_ids.get(port_id) == "":
                    continue
                ifname = port_ids.get(port_id)
                for i in interfaces:
                    if i["name"] == ifname:
                        if (port_id == untagged) and (untagged != "None"):
                            i["subinterfaces"][0]["untagged_vlan"] = vlan_id
                        elif "tagged_vlans" in i["subinterfaces"][0]:
                            i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                        else:
                            i["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
                        break

        return [{"interfaces": interfaces}]
