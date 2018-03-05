# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DGS3100.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "DLink.DGS3100.get_interfaces"
    interface = IGetInterfaces

    rx_ipif = re.compile(
        r"Interface\s*Name\s*: System\s*\nIP\s*Address\s*:\s*"
        r"(?P<ip_address>\S+)\s+\(\S+\)\s*\nSubnet\s*Mask\s*:\s*"
        r"(?P<ip_subnet>\S+)\s*\nVlan\s*Name\s*:\s*(?P<vlan_name>\S+)\s*\n"
        r"Member\s*port\s*:\s*(\S*)\s*\nAdmin.\s*State\s*:\s*"
        r"(?P<admin_state>Enabled|Disabled)\s*\nLink\s*Status\s*:\s*"
        r"(?P<oper_status>Link\s*Up|Link\s*Down)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )
    rx_link_up = re.compile(r"Link\s*UP", re.IGNORECASE)
    rx_lldp_gs = re.compile(r"LLDP Status\s+: Enabled")
    rx_lldp = re.compile(
        r"Port\s*ID\s*:\s*(?P<ipif>\S+)\s*\n\s*\-+\s*\nAdmin\s*Status\s*:\s*"
        r"(?:Tx_and_Rx|Tx_only|Rx_only)")
    rx_ports = re.compile(
        r"^\s*(?P<port>(?:ch|\d+:)\d+)\s*(?P<admin_state>Enabled|Disabled)\s+"
        r"(?P<admin_speed>Auto|10M|100M|1000M)/"
        r"((?P<admin_duplex>Half|Full|Auto)/)?"
        r"(?P<admin_flowctrl>Enabled|Disabled|Auto)\s+(?P<status>Link Down)?"
        r"((?P<speed>10M|100M|1000M)/(?P<duplex>Half|Full)/"
        r"(?P<flowctrl>None|802.3x|Disabled|Enabled))?\s+"
        r"(?P<addr_learning>Enabled|Disabled)\s*$", re.MULTILINE)
    rx_descrs = re.compile(
        r"^(?P<port>\d+:\d+)\s+(?P<description>\S.+)$",
        re.MULTILINE)
    rx_vlan = re.compile(
        r"VID\s*:\s*(?P<vlan_id>\d+)\s+VLAN\s*Name\s+:\s*(?P<vlan_name>\S+)"
        r"\s*\nVLAN\s*TYPE\s+:\s+(?P<vlan_type>\S+)\s*\nMember\s*ports\s*:\s*"
        r"(?P<member_ports>\S*)\s*\nStatic\s*ports\s*:\s*(?P<static_ports>\S*)"
        r"\s*\nUntagged\s*ports\s*:\s*(?P<untagged_ports>\S*)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):

        # Get portchannels
        portchannel_members = {}
        portchannel_interface = []
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            portchannel_interface += [i]
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        lldp = []
        try:
            c = self.cli("show lldp")
        except self.CLISyntaxError:
            c = ""
        lldp_enable = self.rx_lldp_gs.search(c) is not None
        if lldp_enable:
            try:
                c = self.cli("show lldp ports")
            except self.CLISyntaxError:
                raise self.NotSupportedError()
            for match in self.rx_lldp.finditer(c):
                lldp += [match.group("ipif")]

        descriptions = {}
        d = self.cli("show ports descr all")
        for s in d.split("\n"):
            match = self.rx_descrs.search(s)
            if match:
                descriptions[match.group("port")] = match.group("description")
        vlans = []
        c = self.cli("show vlan")
        for match in self.rx_vlan.finditer(c):
            members = self.expand_interface_range(
                self.profile.open_brackets(match.group("member_ports")))
            tagged_ports = []
            untagged_ports = self.expand_interface_range(
                self.profile.open_brackets(match.group("untagged_ports")))
            for p in members:
                if not(p in untagged_ports):
                    tagged_ports += [p]
            vlans += [{
                "vlan_id": int(match.group("vlan_id")),
                "vlan_name": match.group("vlan_name"),
                "vlan_type": match.group("vlan_type"),
                "tagged_ports": tagged_ports,
                "untagged_ports": untagged_ports
            }]

        interfaces = []
        c = self.cli("show ports all")
        for match in self.rx_ports.finditer(c):
            ifname = match.group("port")
            i = {
                "name": ifname,
                "type": "physical",
                "admin_status": match.group("admin_state") == "Enabled",
                "oper_status": match.group("status") is None,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": match.group("admin_state") == "Enabled",
                    "oper_status": match.group("status") is None,
                    # "ifindex": 1,
                    "enabled_afi": ["BRIDGE"]
                }]
            }
            desc = descriptions.get(ifname, '')
            if desc != '' and desc != 'null':
                i.update({"description": desc})
                i['subinterfaces'][0].update({"description": desc})
            tagged_vlans = []
            for v in vlans:
                if ifname in v['tagged_ports']:
                    tagged_vlans += [v['vlan_id']]
                if ifname in v['untagged_ports']:
                    i['subinterfaces'][0]["untagged_vlan"] = v['vlan_id']
            if len(tagged_vlans) != 0:
                i['subinterfaces'][0]['tagged_vlans'] = tagged_vlans
            if lldp_enable and ifname in lldp:
                i["enabled_protocols"] += ["LLDP"]
            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                i["aggregated_interface"] = ai
                i["enabled_protocols"] += ["LACP"]
                i['subinterfaces'][0].update({"enabled_afi": []})
            # Portchannel interface
            if ifname in portchannel_interface:
                i["type"] = "aggregated"
            interfaces += [i]

        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        ipif = self.cli("show ipif")
        for match in self.rx_ipif.finditer(ipif):
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            oper_status = re.match(self.rx_link_up, o_status) is not None
            i = {
                "name": "System",
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": "System",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "enabled_afi": ["IPv4"]
                }]
            }
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            vlan_name = match.group("vlan_name")
            for v in vlans:
                if vlan_name == v['vlan_name']:
                    i['subinterfaces'][0]["vlan_ids"] = [v['vlan_id']]
                    break
            i['subinterfaces'][0]["mac"] = mac
            interfaces += [i]
        return [{"interfaces": interfaces}]
