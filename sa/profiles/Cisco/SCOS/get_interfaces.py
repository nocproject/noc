# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SCOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.lib.ip import IPv4
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces, MACAddressParameter


class Script(NOCScript):
    """
    Cisco.SCOS.get_interfaces

    """
    name = "Cisco.SCOS.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 240

    rx_int = re.compile(r"ifIndex.\d+\s+=\s+(?P<ifindex>\d+)\n"
        r"\s*ifDescr.\d+\s+=\s+(?P<ifname>\S+)\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_stat = re.compile(r"ifAdminStatus.\d+\s+=\s+(?P<a_stat>\d)\n"
        r"ifOperStatus.\d+\s+=\s+(?P<o_stat>\d)\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_mac = re.compile(r"ifPhysAddress.\d+\s+=\s+"
        r"(?P<mac>\w{2}\s\w{2}\s\w{2}\s\w{2}\s\w{2}\s\w{2})\s+\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_ip = re.compile(r"ip address:\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\n"
        r"subnet mask:\s+(?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\n",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        ifaces = {}
        #Get interfaces from mibs
        try:
            c = self.cli("sh snmp MIB MIB-II interfaces")
        except self.CLISyntaxError:
            return {}
        r = {}
        for l in c.split("\n\n"):
            ip_addr = []
            if l.startswith("ifName"):
                continue
            match = self.rx_int.search(l.strip())
            if match:
                match_s = self.rx_stat.search(l.strip())
                if match_s:
                    name = self.profile.convert_interface_name(match.group("ifname"))
                    i = int(match.group("ifindex"))
                    match_m = self.rx_mac.search(l.strip())
                    enabled_afi = ["BRIDGE"]
                    if match_m:
                        mac = MACAddressParameter().clean(match_m.group("mac").replace(" ", ":"))
                        ip_addr = self.get_ipaddr(name)
                        if ip_addr:
                            enabled_afi = ["IPv4"]
                    else:
                        mac = None

                    #Create sub
                    sub = {
                        "name": name,
                        "enabled_protocols": [],
                        "ifindex": i,
                        "admin_status": match_s.group("a_stat") == "1",
                        "oper_status": match_s.group("o_stat") == "1",
                        "enabled_afi": enabled_afi,
                    }
                    if ip_addr:
                        sub["ipv4_addresses"] = ip_addr
                    if mac:
                        sub["mac"] = mac

                    #Create iface
                    ifaces[name] = {
                        "name": name,
                        "enabled_protocols": [],
                        "admin_status": match_s.group("a_stat") == "1",
                        "oper_status": match_s.group("o_stat") == "1",
                        "type": "physical",
                        "ifindex": i,
                        "subinterfaces": [sub],
                    }
                    if mac:
                        ifaces[name]["mac"] = mac
        # Create afi
        afi_m = {
            "forwarding_instance": "Managment",
            "type": "ip",
            "interfaces": []
        }
        afi_b = {
            "forwarding_instance": "DPI",
            "type": "bridge",
            "interfaces": []
        }

        for i in ifaces:
            if ifaces[i].get("mac"):
                afi_m["interfaces"] += [ifaces[i]]
            else:
                afi_b["interfaces"] += [ifaces[i]]

        return [afi_m, afi_b]

    def get_ipaddr(self, name):
        try:
            v = self.cli("show interface " + name)
        except self.CLISyntaxError:
            return
        match = self.rx_ip.match(v)
        if match:
            return [IPv4(match.group("ip"), netmask=match.group("mask")).prefix]
