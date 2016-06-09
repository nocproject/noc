# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from collections import defaultdict
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.text import ranges_to_list
from noc.lib.ip import IPv4


class Script(BaseScript):
    name = "Raisecom.ROS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_vlans = re.compile(r"""
        Port:\s(?P<name>\d+)\s*\n
        Administrative\sMode:\s*(?P<adm_mode>.*)\n
        Operational\sMode:\s*(?P<op_mode>.*)\n
        Access\sMode\sVLAN:\s*(?P<untagged_vlan>.*)\n
        Administrative\sAccess\sEgress\sVLANs:\s*(?P<mvr_vlan>.*)\n
        Operational\sAccess\sEgress\sVLANs:\s*(?P<op_eg_vlan>.*)\n
        Trunk\sNative\sMode\sVLAN:\s*(?P<trunk_native_vlan>.*)\n
        Trunk\sNative\sVLAN:\s*(?P<trunk_native_vlan_mode>.*)\n
        Administrative\sTrunk\sAllowed\sVLANs:\s*(?P<adm_trunk_allowed_vlan>.*)\n
        Operational\sTrunk\sAllowed\sVLANs:\s*(?P<op_trunk_allowed_vlan>.*)\n
        Administrative\sTrunk\sUntagged\sVLANs:\s*(?P<adm_trunk_untagged_vlan>.*)\n
        Operational\sTrunk\sUntagged\sVLANs:\s*(?P<op_trunk_untagged_vlan>.*)
        """, re.VERBOSE)
    rx_iface = re.compile(
        r"^\s*(?P<iface>\d+)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)\s+"
        r"(?P<vid>\d+)\s+(?P<oper_status>\S+)\s*\n", re.MULTILINE)
    rx_lldp = re.compile(
        "LLDP enable status:\s+enable.+\n"
        "LLDP enable ports:\s+(?P<ports>\S+)\n", re.MULTILINE)

    def parse_vlans(self, section):
        r = {}
        match = re.search(self.rx_vlans, section)
        if match:
            r = match.groupdict()
        return r

    def execute(self):
        lldp_ifaces = []
        match = re.search(self.rx_lldp, self.cli("show lldp local config"))
        if match:
            lldp_ifaces = self.expand_rangelist(match.group("ports"))
        ifaces = []
        v = self.cli("show interface port description")
        for line in v.splitlines()[2:-1]:
            i = {
                "name": int(line[:8]),
                "type": "physical",
                "subinterfaces": []
            }
            if str(line[8:]) != "-":
                i["description"] = str(line[8:])
            if i["name"] in lldp_ifaces:
                i["enabled_protocols"] = ["LLDP"]
            ifaces.append(i)

        statuses = []
        v = self.cli("show interface port")
        for line in v.splitlines()[5:]:
            i = {
                "name": int(line[:6]),
                "admin_status": "enable" in line[7:14],
                "oper_status": "up" in line[14:29]
            }
            statuses.append(i)

        vlans = []
        v = self.cli("show interface port switchport")
        for section in v.split("\n\n"):
            if not section:
                continue
            vlans.append(self.parse_vlans(section))

        d = defaultdict(dict)

        for l in (statuses, ifaces):
            for elem in l:
                d[elem['name']].update(elem)
        l3 = d.values()

        for port in l3:
            name = port["name"]
            port["subinterfaces"] = [{
                "name": str(name),
                "enabled_afi": ["BRIDGE"],
                "admin_status": port["admin_status"],
                "oper_status": port["oper_status"],
                "tagged_vlans": [],
                "untagged_vlan": [int(vlan['untagged_vlan']) for vlan in vlans if int(vlan['name']) == name][0]
            }]
            if "description" in port:
                port["subinterfaces"][0]["description"] = port["description"]
            tvl = [vlan['op_trunk_allowed_vlan'] for vlan in vlans if int(vlan['name']) == name][0]
            #if 'n/a' not in tvl:
            #    port["subinterfaces"][0]['tagged_vlans'] = ranges_to_list(tvl)

        if_descr = []
        v = self.cli("show interface ip description")
        for line in v.splitlines()[2:-1]:
            i = {
                "name": int(line[:9]),
                "description": str(line[9:])
            }
            if_descr.append(i)
        v = self.profile.get_version(self)
        mac = v["mac"]
        """
        XXX: This is a dirty hack !!!
        I do not know, how get ip interface MAC address
        """
        v = self.cli("show interface ip 0")
        for match in self.rx_iface.finditer(v):
            ifname = match.group("iface")
            i = {
                "name": "ip%s" % ifname,
                "type": "SVI",
                "oper_status": match.group("oper_status") == "active",
                "admin_status": match.group("oper_status") == "active",
                "mac": mac,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": "ip%s" % ifname,
                    "oper_status": match.group("oper_status") == "active",
                    "admin_status": match.group("oper_status") == "active",
                    "mac": mac,
                    "vlan_ids": [int(match.group('vid'))],
                    "enabled_afi": ['IPv4']
                }]
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            for q in if_descr:
                if str(q["name"]).strip() == ifname:
                    i['description'] = q['description']
                    i['subinterfaces'][0]["description"] = q['description']
            l3 += [i]
            # parse only "0" interface
            break

        return [{"interfaces": l3}]

