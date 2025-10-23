# ---------------------------------------------------------------------
# Qtech.QOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import ranges_to_list
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Qtech.QOS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_port = re.compile(r"^P(?P<port>\d+)\s+", re.MULTILINE)
    rx_vlan = re.compile(
        r"^Operational Mode: (?P<op_mode>\S+)\s*\n"
        r"^Access Mode VLAN:\s*(?P<access_vlan>\d+)\s*\n"
        r"^Administrative Access Egress VLANs:.*\n"
        r"^Operational Access Egress VLANs:.*\n"
        r"^Trunk Native Mode VLAN:\s*(?P<trunk_native_vlan>.*)\n"
        r"^Administrative Trunk Allowed VLANs:.*\n"
        r"^Operational Trunk Allowed VLANs:\s*(?P<op_vlans>.*)\n"
        r"^Administrative Trunk Untagged VLANs:.*\n"
        r"^Operational Trunk Untagged VLANs:\s*(?P<op_untagged>.*)\n",
        re.MULTILINE,
    )
    rx_ip_iface = re.compile(
        r"^\s*(?P<iface>\d+)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)\s+assigned\s+primary\s*\n",
        re.MULTILINE,
    )
    rx_vlans_ip = re.compile(r"^\s*(?P<iface>\d+)\s+(?P<vlan_id>\d+|none)", re.MULTILINE)

    def execute_cli(self):
        interfaces = []
        v = self.cli("show lldp local config")
        for port in self.rx_port.finditer(v):
            port_no = port.group("port")
            c = self.cli("show interface port-list %s switchport" % port_no)
            match = self.rx_vlan.search(c)
            iface = {"name": "port%s" % port_no, "type": "physical"}
            sub = {"name": "port%s" % port_no, "enabled_afi": ["BRIDGE"]}
            if match.group("op_mode") in ["trunk", "hybrid"]:
                sub["untagged_vlan"] = int(match.group("trunk_native_vlan"))
                sub["tagged_vlans"] = ranges_to_list(match.group("op_vlans"))

            else:
                sub["untagged_vlan"] = int(match.group("access_vlan"))

            iface["subinterfaces"] = [sub]
            interfaces += [iface]

        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        v = self.cli("show interface ip")
        for match in self.rx_ip_iface.finditer(v):
            ifname = match.group("iface")
            i = {
                "name": "ip%s" % ifname,
                "type": "SVI",
                "mac": mac,
                "enabled_protocols": [],
                "subinterfaces": [{"name": "ip%s" % ifname, "mac": mac, "enabled_afi": ["IPv4"]}],
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            interfaces += [i]
        v = self.cli("show interface ip vlan")
        for match in self.rx_vlans_ip.finditer(v):
            vlan_id = match.group("vlan_id")
            if vlan_id == "none":
                continue
            ifname = "ip%s" % match.group("iface")
            for i in interfaces:
                if i["name"] == ifname:
                    i["subinterfaces"][0]["vlan_ids"] = vlan_id
                    break
        return [{"interfaces": interfaces}]
