# ---------------------------------------------------------------------
# Eltex.MES24xx.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table
from noc.core.validators import is_vlan


class Script(BaseScript):

    name = "Eltex.MES24xx.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifname>\S+|(?:te|gi|fa|ex|po|vl)[a-z]*\s\d+\S*) (?P<admin_status>up|down), "
        r"line protocol is (?P<oper_status>up|down) .+\n"
        r"(?:^Bridge Port Type: .+\n)?"
        r"(?:^\s*\n)?"
        r"^Interface SubType: .+\n"
        r"(^(?:Interface Alias|Description): (?P<descr>.+)\n)?"
        r"(?:^\s*\n)?"
        r"(^Hardware Address is (?P<mac>\S+)\s*\n)?"
        r"(^MTU\s+(?P<mtu>\d+) bytes,.+\s*\n)?",
        re.MULTILINE,
    )
    rx_ip_iface = re.compile(
        r"^(?P<ifname>\S+|vlan \d+) is (?P<admin_status>up|down), "
        r"line protocol is (?P<oper_status>up|down)\s*\n"
        r"^Internet Address is (?P<ip>\d+\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        interfaces = []
        v = self.cli("show interfaces")
        for match in self.rx_iface.finditer(v):
            ifname = match.group("ifname")
            admin_status = match.group("admin_status") == "up"
            oper_status = match.group("oper_status") == "up"
            iface = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_status": admin_status,
                "oper_status": oper_status,
            }
            sub = {"name": ifname, "admin_status": admin_status, "oper_status": oper_status}
            if iface["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
                if ifname.lower().startswith("gi"):
                    sw_ifname = "gigabitethernet %s" % ifname[2:]
                elif ifname.lower().startswith("fa"):
                    sw_ifname = "fastethernet %s" % ifname[2:]
                elif ifname.lower().startswith("ex"):
                    sw_ifname = "extreme-ethernet %s" % ifname[2:]
                elif ifname.lower().startswith("te"):
                    sw_ifname = "tengigabitethernet %s" % ifname[2:]
                elif ifname.lower().startswith("po"):
                    sw_ifname = "port-channel %s" % ifname[2:]
                c = self.cli("show interfaces switchport %s" % sw_ifname)
                for i in parse_table(c, footer="^Forbidden VLANs:"):
                    vlan_id = i[0]
                    if not is_vlan(vlan_id):
                        continue
                    if i[2] == "Untagged":
                        sub["untagged_vlan"] = vlan_id
                    elif "tagged_vlans" in sub:
                        sub["tagged_vlans"] += [vlan_id]
                    else:
                        sub["tagged_vlans"] = [vlan_id]
            if iface["name"].startswith("vlan"):
                sub["vlan_ids"] = iface["name"][4:]
            if match.group("mac"):
                mac = match.group("mac").strip()
                iface["mac"] = mac
                sub["mac"] = mac
            if match.group("descr"):
                descr = match.group("descr").strip()
                iface["description"] = descr
                sub["description"] = descr
            iface["subinterfaces"] = [sub]
            interfaces += [iface]
        v = self.cli("show ip interface")
        for match in self.rx_ip_iface.finditer(v):
            ifname = match.group("ifname")
            for i in interfaces:
                if i["name"] == ifname:
                    i["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                    i["subinterfaces"][0]["ipv4_addresses"] = [match.group("ip")]
                    break
        return [{"interfaces": interfaces}]

    def execute(self, **kwargs):
        if self.is_mes14_24:
            # Model 14XX/24XX
            self.always_prefer = "S"
        return super().execute()
