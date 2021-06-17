# ---------------------------------------------------------------------
# Eltex.LTE.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.LTE.get_interfaces"
    interface = IGetInterfaces

    rx_mac1 = re.compile(r"^Port (?P<port>\d+) MAC address: (?P<mac>\S+)", re.MULTILINE)
    rx_mac2 = re.compile(r"MAC address:\s*\n^\s+(?P<mac>\S+)", re.MULTILINE)
    rx_vlan = re.compile(
        r"^Interface (?P<port>\d+)\s*\n"
        r"^\s+PVID:\s+\d+\s*\n"
        r"^\s+Frame types:\s+\S+\s*\n"
        r"^\s+Ingress filtering:\s+\S+\s*\n"
        r"^\s+Member of VLANs:\s*\n"
        r"^\s+tagged:\s+(?P<tagged>.+)\n"
        r"^\s+untagged:\s+(?P<untagged>\d+|none)",
        re.MULTILINE | re.DOTALL,
    )

    rx_ip = re.compile(r"\n\nIP address:\s+(?P<ip>\d+\S+)")
    rx_mgmt_ip = re.compile(
        r"^Management interface:( \((?P<state>\S+)\))?\s*\n"
        r"^IP address:\s+(?P<ip>\d+\S+)\s*\n"
        r"(^Default gateway:.+\n)?"
        r"^VID:\s+(?P<vlan_id>\d+|none)",
        re.MULTILINE,
    )
    rx_mac = re.compile(r"^\s+MAC address: (?P<mac>\S+)", re.MULTILINE)
    rx_status = re.compile(r"^.+\d\s+(?P<oper_status>up|down|off)", re.MULTILINE)

    def normalize_ifname(self, port):
        port = port.strip()
        while port.find("  ") != -1:
            port = port.replace("  ", " ")
        while port.find("- ") != -1:
            port = port.replace("- ", "-")
        return port

    def create_iface(self, i, iftype):
        ifname = " ".join(i[0].split())
        if not ifname.startswith(iftype):
            return None
        pvid = i[1]
        if i[4] not in ["none", "N/S"]:
            tagged = self.expand_rangelist(i[4])
        else:
            tagged = []
        untagged = i[5]
        if untagged in ["none", "N/S"]:
            untagged = pvid
        iface = {
            "name": ifname,
            "type": "physical",
            "subinterfaces": [{"name": ifname, "enabled_afi": ["BRIDGE"]}],
        }
        if untagged != "N/S":
            iface["subinterfaces"][0]["untagged_vlan"] = int(untagged)
        if tagged:
            iface["subinterfaces"][0]["tagged_vlans"] = tagged
        return iface

    def execute(self):
        interfaces = []
        macs = {}
        tagged_vlans = {}
        untagged_vlans = {}
        try:
            with self.profile.switch(self):
                cmd = self.cli("show interfaces mac-address")
                for match in self.rx_mac1.finditer(cmd):
                    macs[match.group("port")] = match.group("mac")
                for line in self.cli("show interfaces vlans").split("\n\n"):
                    match = self.rx_vlan.search(line)
                    if match:
                        if match.group("tagged") != "none":
                            tagged_vlans[match.group("port")] = self.expand_rangelist(
                                match.group("tagged")
                            )
                        if match.group("untagged") != "none":
                            untagged_vlans[match.group("port")] = match.group("untagged")
                cmd = self.cli("show version")
                match = self.rx_mac2.search(cmd)
                if match:
                    ip_mac = match.group("mac")
                else:
                    ip_mac = ""
            ports = self.scripts.get_interface_status()
            for i in ports:
                iface = {
                    "name": i["interface"],
                    "type": "physical",
                    "oper_status": i["status"],
                    "mac": macs[i["interface"]],
                    "subinterfaces": [
                        {
                            "name": i["interface"],
                            "oper_status": i["status"],
                            "enabled_afi": ["BRIDGE"],
                            "mac": macs[i["interface"]],
                        }
                    ],
                }
                t = tagged_vlans.get(i["interface"])
                if t:
                    iface["subinterfaces"][0]["tagged_vlans"] = t
                u = untagged_vlans.get(i["interface"])
                if u:
                    iface["subinterfaces"][0]["untagged_vlan"] = u
                interfaces += [iface]
        except self.CLISyntaxError:
            # We are already in `switch` context
            c = self.cli("show vlan", cached=True)
            t = parse_table(c, allow_wrap=True, footer="dummy footer")
            for i in t:
                vlan_id = i[0]
                if i[2] != "none":
                    tagged = i[2].split(", ")
                    for port in tagged:
                        ifname = self.normalize_ifname(port)
                        found = False
                        for iface in interfaces:
                            if iface["name"] == ifname:
                                if "tagged_vlans" in iface["subinterfaces"][0]:
                                    iface["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                                else:
                                    iface["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
                                found = True
                                break
                        if not found:
                            iface = {
                                "name": ifname,
                                "type": "physical",
                                "subinterfaces": [
                                    {
                                        "name": ifname,
                                        "enabled_afi": ["BRIDGE"],
                                        "tagged_vlans": [vlan_id],
                                    }
                                ],
                            }
                            interfaces += [iface]
                if i[3] != "none":
                    untagged = i[3].split(", ")
                    for port in untagged:
                        ifname = self.normalize_ifname(port)
                        found = False
                        for iface in interfaces:
                            if iface["name"] == ifname:
                                iface["subinterfaces"][0]["untagged_vlan"] = vlan_id
                                found = True
                                break
                        if not found:
                            iface = {
                                "name": ifname,
                                "type": "physical",
                                "subinterfaces": [
                                    {
                                        "name": ifname,
                                        "enabled_afi": ["BRIDGE"],
                                        "untagged_vlan": vlan_id,
                                    }
                                ],
                            }
                            interfaces += [iface]
            for i in interfaces:
                c = self.cli("show interfaces mac-address %s" % i["name"])
                match = self.rx_mac.search(c)
                if match:
                    i["mac"] = match.group("mac")
                    i["subinterfaces"][0]["mac"] = match.group("mac")
                try:
                    c = self.cli("show interfaces status %s" % i["name"])
                    match = self.rx_status.search(c)
                    i["oper_status"] = match.group("oper_status") == "up"
                    i["subinterfaces"][0]["oper_status"] = match.group("oper_status") == "up"
                    i["admin_status"] = match.group("oper_status") != "off"
                    i["subinterfaces"][0]["admin_status"] = match.group("oper_status") != "off"
                except self.CLISyntaxError:
                    pass
            c = self.cli("exit")  # manually exit from `switch` context
        cmd = self.cli("show system information")
        match = self.rx_ip.search(cmd)
        if match:
            iface = {
                "name": "ip",
                "type": "SVI",
                "subinterfaces": [
                    {"name": "ip", "enabled_afi": ["IPv4"], "ipv4_addresses": [match.group("ip")]}
                ],
            }
            if ip_mac:
                iface["mac"] = ip_mac
                iface["subinterfaces"][0]["mac"] = ip_mac
            interfaces += [iface]
        match = self.rx_mgmt_ip.search(cmd)
        if match:
            iface = {
                "name": "mgmt",
                "type": "management",
                "oper_status": match.group("state") == "enabled",
                "admin_status": match.group("state") == "enabled",
                "subinterfaces": [
                    {
                        "name": "mgmt",
                        "oper_status": match.group("state") == "enabled",
                        "admin_status": match.group("state") == "enabled",
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [match.group("ip")],
                    }
                ],
            }
            if match.group("vlan_id") != "none":
                iface["subinterfaces"][0]["vlan_id"] = [match.group("vlan_id")]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
