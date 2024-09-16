# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.validators import is_int


class Script(BaseScript):
    name = "3Com.SuperStack3.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^(?P<port>\d+\:\d+)\s+(?P<status>Active|Inactive)\s+" r"(?P<stp>\S+)", re.MULTILINE
    )
    rx_stp = re.compile(r"^StpState:\s+Enabled", re.MULTILINE)
    rx_lacp = re.compile(r"^LACP State:\s+Disabled", re.MULTILINE)
    rx_vlan = re.compile(r"^(?P<vlan_id>\d+)\s+.+\s+(?P<mode>\S+)\s+\S+\s*\n", re.MULTILINE)
    rx_ipif = re.compile(
        r"^\d+\s+(?P<name>\S+)\s+(?P<ip>\S+)\s+(?P<mask>\S+)\s+(?P<status>\S+)\s+"
        r"(?P<vlan_id>(?:\d+|n/a))\s*\n",
        re.MULTILINE,
    )

    def execute(self):
        interfaces = []
        ports = []
        gstp = bool("Network | STP" in self.scripts.get_capabilities())
        v = self.profile.get_hardware(self)
        mac = v["mac"]
        v = self.cli("bridge port summary all")
        for match in self.rx_port.finditer(v):
            ports += [{"name": match.group("port"), "status": match.group("status") == "Active"}]
        for p in ports:
            i = {
                "name": p["name"],
                "type": "physical",
                "oper_status": p["status"],
                "enabled_protocols": [],
                "subinterfaces": [
                    {"name": p["name"], "oper_status": p["status"], "enabled_afi": ["BRIDGE"]}
                ],
            }
            v = self.cli("bridge port detail %s" % p["name"])
            if gstp and self.rx_stp.search(v):
                i["enabled_protocols"] += ["STP"]
            if not self.rx_lacp.search(v):
                i["enabled_protocols"] += ["LACP"]
            for match in self.rx_vlan.finditer(v):
                vlan_id = int(match.group("vlan_id"))
                if match.group("mode") == "Untagged":
                    i["subinterfaces"][0]["untagged_vlan"] = vlan_id
                elif "tagged_vlans" in i["subinterfaces"][0]:
                    i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                else:
                    i["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
            interfaces += [i]
        v = self.cli("protocol ip interface summary all")
        for match in self.rx_ipif.finditer(v):
            status = bool(match.group("status") == "Up")
            i = {
                "name": match.group("name"),
                "type": "SVI",
                "admin_status": status,
                "oper_status": status,
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": match.group("name"),
                        "admin_status": status,
                        "oper_status": status,
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            if is_int(match.group("vlan_id")):
                vlan_id = int(match.group("vlan_id"))
                i["subinterfaces"][0]["vlan_ids"] = [vlan_id]
                i["mac"] = mac
                i["subinterfaces"][0]["mac"] = mac
            elif match.group("name") == "SLIP":
                i["type"] = "tunnel"
                i["tunnel"] = {}
                i["tunnel"]["type"] = "SLIP"
                i["tunnel"]["local_address"] = match.group("ip")
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            interfaces += [i]
        return [{"interfaces": interfaces}]
