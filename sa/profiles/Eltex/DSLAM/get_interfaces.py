# ---------------------------------------------------------------------
# Eltex.DSLAM.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.validators import is_int
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Eltex.DSLAM.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(r"(?P<port>cpu|sfp\d*|dsl\d+)")
    rx_adsl_port = re.compile(r"(?P<port>p\d+)")
    rx_adsl_sub1 = re.compile(
        r"(?P<port>p\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\S+\s+\S+\s+(?P<vlan_id>(?:\d+|\-+))"
    )
    rx_adsl_sub2 = re.compile(
        r"\d+\s+(?P<port>p\d+)\s+(?P<vlan_id>\d+)\s+\d+\s+\S+\s+\S+\s+\d+\s+(?P<vpi>\d+)\s+(?P<vci>\d+)"
    )
    rx_ip = re.compile(
        r"^\s+(?:Control vid|Mgmt vlan):\s+(?P<vlan_id>\d+)\s*\n"
        r"^\s+IP address:\s+(?P<ip_address>\d+\S+)\s*\n"
        r"^\s+Server IP:\s+\S+(?:\n\S+.*?)?\n"
        r"^\s+MAC address:\s+(?P<mac>\S+)\s*\n"
        r"^\s+Netmask:\s+(?P<ip_subnet>\d+\S+)\s*.*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        interfaces = []
        try:
            cmd = self.cli("switch show port state")
        except self.CLISyntaxError:
            cmd = self.cli("switch port status")

        items = self.profile.iter_items(cmd)
        try:
            cmd = self.cli("switch show vlan table all")
        except self.CLISyntaxError:
            cmd = self.cli("switch show vlan all")
        items1 = self.profile.iter_items(cmd)
        for i in items[0]:
            if i in ["STATE", "Port"]:
                continue
            oper_status = items[1][items[0].index(i)] == "UP"
            if i == "cpu":
                iface = {
                    "name": i,
                    "type": "SVI",
                    "oper_status": oper_status,
                    "subinterfaces": [
                        {"name": i, "oper_status": oper_status, "enabled_afi": ["IPv4"]}
                    ],
                }
                try:
                    v = self.cli("system show net settings")
                except self.CLISyntaxError:
                    v = self.cli("cpu show net settings")
                match = self.rx_ip.search(v)
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                iface["subinterfaces"][0]["vlan_ids"] = [match.group("vlan_id")]
                iface["mac"] = match.group("mac")
                iface["subinterfaces"][0]["mac"] = match.group("mac")
                interfaces += [iface]
            else:
                column = items1[0].index(i)
                ifname = "s%s" % i if i.startswith("p") else i
                iface = {"name": ifname, "type": "physical", "oper_status": oper_status}
                sub = {"name": ifname, "oper_status": oper_status, "enabled_afi": ["BRIDGE"]}
                for ii in range(1, len(items1)):
                    vlan_id = int(items1[ii][0])
                    vlan_type = items1[ii][column].upper()
                    if vlan_type == "DISC":
                        sub["untagged_vlan"] = vlan_id
                    elif "tagged_vlans" in sub:
                        sub["tagged_vlans"] += [vlan_id]
                    else:
                        sub["tagged_vlans"] = [vlan_id]
                iface["subinterfaces"] = [sub]
                interfaces += [iface]
        cmd = self.cli("adsl show port oper status")
        has_show_entry = True
        for match in self.rx_adsl_port.finditer(cmd):
            ifname = match.group("port")
            ifname = ifname.replace("p0", "p")
            iface = {"name": ifname, "type": "physical", "subinterfaces": []}
            if has_show_entry:
                try:
                    v = self.cli("enpu show entry %s" % ifname)
                    rx_adsl_sub = self.rx_adsl_sub1
                except self.CLISyntaxError:
                    has_show_entry = False
            if not has_show_entry:
                v = self.cli("enpu show upstream entry %s" % ifname)
                rx_adsl_sub = self.rx_adsl_sub2
                ifnumber = 0
                for match1 in rx_adsl_sub.finditer(v):
                    ifnumber += 1
                    sub = {
                        "name": "%s.%s" % (ifname, ifnumber),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "vpi": match1.group("vpi"),
                        "vci": match1.group("vci"),
                    }
                    if is_int(match1.group("vlan_id")):
                        sub["vlan_ids"] = [match1.group("vlan_id")]
                    iface["subinterfaces"] += [sub]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
