# ---------------------------------------------------------------------
# AlliedTelesis.AT8000.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "AlliedTelesis.AT8000.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^Port # (?P<port>\d+) Information:\s*\n"
        r"\s*\n"
        r"\s*Description\s*\.+(?P<descr>.+)\n"
        r"\s*Status.+\n"
        r"\s*Link State\s*\.+ (?P<oper_status>Up|Down)\s*\n"
        r"\s*Negotiation.+\n"
        r"\s*Speed.+\n"
        r"\s*Duplex.+\n"
        r"\s*Flow Control.+\n"
        r"\s*MDIO Mode.+\n"
        r"\s*Back Pressure.+\n"
        r"\s*Broadcast Limit.+\n"
        r"\s*MAC Threshold.+\n"
        r"\s*PVID\s*\.+ (?P<pvid>\d+)\s*\n",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"^\s+IP Address\s*.+ (?P<ip>\S+)\s*\n" r"^\s+Net Mask\s*.+ (?P<mask>\S+)\n", re.MULTILINE
    )

    def execute_cli(self):
        ifaces = []
        v = self.cli("show switch port")
        for match in self.rx_port.finditer(v):
            port = match.group("port")
            i = {
                "name": port,
                "type": "physical",
                "admin_status": True,
                "oper_status": match.group("oper_status") == "Up",
                "snmp_ifindex": int(port),  # Found in AT-8024
                "subinterfaces": [
                    {
                        "name": port,
                        "admin_status": True,
                        "oper_status": match.group("oper_status") == "Up",
                        "enabled_afi": ["BRIDGE"],
                        "untagged_vlan": match.group("pvid"),
                    }
                ],
            }
            descr = match.group("descr").strip()
            if descr:
                i["description"] = descr
                i["subinterfaces"][0]["description"] = descr
            ifaces += [i]
        v = self.cli("show vlan", cached=True)
        for match in self.profile.rx_vlan.finditer(v):
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
        match = self.rx_ip.search(v)
        ip_address = "%s/%s" % (match.group("ip"), IPv4.netmask_to_len(match.group("mask")))

        i = {
            "name": "mgmt",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "subinterfaces": [
                {
                    "name": "mgmt",
                    "admin_status": True,
                    "oper_status": True,
                    "ipv4_addresses": [ip_address],
                    "enabled_afi": ["IPv4"],
                }
            ],
        }
        ifaces += [i]
        return [{"interfaces": ifaces}]
