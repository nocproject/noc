# ---------------------------------------------------------------------
# AlliedTelesis.AT9900.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_port = re.compile(
        r" Port.+ (?P<port>\d+)\n"
        r"\s*Description\s*\.+ (?P<descr>.+)\n"
        r"\s*Status.+\n"
        r"\s*Link State\s*\.+ (?P<oper_status>Up|Down)\s*\n",
        re.MULTILINE,
    )
    rx_vlan = re.compile(
        r"\s*Name\s*.+ (?P<name>\S+)\s*\n"
        r"\s*Identifier\s*.+ (?P<vlan_id>\d+)\s*\n"
        r"\s*Status.+\n"
        r"\s*Type.+\n"
        r"\s*Private.+\n"
        r"\s*Nested.+\n"
        r"\s*Untagged ports.+ (?P<untagged>.+)\n"
        r"\s*Tagged ports.+ (?P<tagged>.+)\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        ifaces = []
        v = self.cli("show switch port")
        for match in self.rx_port.finditer(v):
            port = "port" + match.group("port")
            i = {
                "name": port,
                "type": self.profile.get_interface_type(port),
                "admin_status": True,
                "oper_status": match.group("oper_status") == "Up",
                "subinterfaces": [
                    {
                        "name": port,
                        "admin_status": True,
                        "oper_status": match.group("oper_status") == "Up",
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            descr = match.group("descr").strip()
            if descr:
                i["description"] = descr
                i["subinterfaces"][0]["description"] = descr
            ifaces += [i]
        v = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(v):
            tagged = match.group("tagged").strip()
            if tagged == "None":
                continue
            vlan_id = int(match.group("vlan_id"))
            tagged = self.expand_rangelist(tagged)
            for ifname in tagged:
                for iface in ifaces:
                    if iface["name"] == str(ifname):
                        sub = iface["subinterfaces"][0]
                        if "tagged_vlans" in sub:
                            sub["tagged_vlans"] += [vlan_id]
                        else:
                            sub["tagged_vlans"] = [vlan_id]
                        break

        v = self.cli("show ip interface")
        ip = ""
        vlan = ""
        for l in v.splitlines():
            line = re.split(r"\s+", l)
            if len(line) > 2:
                if line[0].startswith("vlan"):
                    vlan = line[0]
                    ip = line[2]
                    continue
                if line[0] == "---" and ip != "":
                    ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(line[2]))
                    mtu = line[3]
                    vlan_id = vlan.replace("vlan", "")
                    i = {
                        "name": vlan,
                        "type": self.profile.get_interface_type(vlan),
                        "admin_status": True,
                        "oper_status": True,
                        "subinterfaces": [
                            {
                                "name": vlan,
                                "admin_status": True,
                                "oper_status": True,
                                "mtu": mtu,
                                "vlan_ids": [vlan_id],
                                "ipv4_addresses": [ip_address],
                                "enabled_afi": ["IPv4"],
                            }
                        ],
                    }
                    ifaces += [i]
        return [{"interfaces": ifaces}]
