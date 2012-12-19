# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    name = "DLink.DGS3100.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 300

    rx_ipif1 = re.compile(r"Interface\s*Name\s*:\s*(?P<ifname>\S+)\s*\nIP\s*Address\s*:\s*(?P<ip_address>\S+)\s+\(\S+\)\s*\nSubnet\s*Mask\s*:\s*(?P<ip_subnet>\S+)\s*\nVlan\s*Name\s*:\s*(?P<vlan_name>\S+)\s*\nMember\s*port\s*:\s*(\S+)\s*\nAdmin.\s*State\s*:\s*(?P<admin_state>Enabled|Disabled)\s*\nLink\s*Status\s*:\s*(?P<oper_status>Link\s*Up|Link\s*Down)\s*\n",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)
    rx_link_up = re.compile(r"Link\s*UP", re.IGNORECASE)
    rx_lldp = re.compile(r"Port\s*ID\s*:\s*(?P<ipif>\S+)\s*\n\s*\-+\s*\nAdmin\s*Status\s*:\s*(?:Tx_and_Rx|Tx_only|Rx_only)")
    rx_igmp = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+"
    r"\d+\s+(?P<state>Enabled)\s+")
    rx_ports=re.compile(r"^\s*(?P<port>\d+(/|:)?\d*)\s*(?P<admin_state>Enabled|Disabled)\s+(?P<admin_speed>Auto|10M|100M|1000M|10G)/((?P<admin_duplex>Half|Full|Auto)/)?(?P<admin_flowctrl>Enabled|Disabled)\s+(?P<status>LinkDown|Link\sDown)?((?P<speed>10M|100M|1000M|10G)/(?P<duplex>Half|Full)/(?P<flowctrl>None|802.3x|Disabled))?\s+(?P<addr_learning>Enabled|Disabled)\s*$",re.MULTILINE)
    rx_descrs=re.compile(r"^\s*(?P<port>\d+(/|:)?\d*)\s*(?P<description>[a-zA-Z0-9_ \-]+)?$",re.MULTILINE)
    rx_vlan = re.compile(r"VID\s*:\s*(?P<vlan_id>\d+)\s+VLAN\s*Name\s+:\s*(?P<vlan_name>\S+)\s*\nVLAN\s*TYPE\s+:\s+(?P<vlan_type>\S+)\s*\nMember\s*ports\s*:\s*(?P<member_ports>\S*)\s*\nStatic\s*ports\s*:\s*(?P<static_ports>\S*)\s*\nUntagged\s*ports\s*:\s*(?P<untagged_ports>\S*)\s*\n",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):
        lldp = []
        try:
            c = self.cli("show lldp")
        except self.CLISyntaxError:
            c = ""
            pass
        lldp_enable = self.rx_lldp_gs.search(c) is not None
        if lldp_enable:
            try:
                c = self.cli("show lldp ports")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_lldp.finditer(c):
                lldp += [match.group("ipif")]
        igmp = []
        try:
            c = self.cli("show igmp")
        except self.CLISyntaxError:
            c = ""
            pass
        for match in self.rx_igmp.finditer(c):
            igmp += [match.group("ipif")]
        ports=[]
        objects=[]
        descriptions={}
        try:
            d=self.cli("show ports descr all")
        except self.CLISyntaxError:
            d=""
            pass
        if d:
            for match in self.rx_descrs.finditer(d):
                descriptions[ match.group("port")]= match.group("description")
        try:
            c=self.cli("show ports all")
        except self.CLISyntaxError:
            c=""
            pass
        if c:
            for match in self.rx_ports.finditer(c):
                objects+=[{
                    "port":match.group("port"),
                    "admin_state":match.group("admin_state") =="Enabled",
                    "admin_speed":match.group("admin_speed"),
                    "admin_duplex":match.group("admin_duplex"),
                    "admin_flowctrl":match.group("admin_flowctrl"),
                    "status":match.group("status") is None,
                    "speed":match.group("speed"),
                    "duplex":match.group("duplex"),
                    "flowctrl":match.group("flowctrl"),
                    "address_learning":match.group("addr_learning").strip(),
                    "desc":descriptions[match.group("port")] if match.group("port") in descriptions else "None"
                }]
        for i in objects:
            ports+=[i]
        vlans = []
        try:
            c=self.cli("show vlan")
        except self.CLISyntaxError:
            c=""
            pass
        if c:
            for match in self.rx_vlan.finditer(c):
                members = self.expand_interface_range(match.group("member_ports").replace("(","").replace(")",""))
                tagged_ports = []
                untagged_ports = \
                    self.expand_interface_range(match.group("untagged_ports").replace("(","").replace(")",""))
                for p in members:
                    if not(p in untagged_ports):
                        tagged_ports +=[p]
                vlans += [{
                    "vlan_id": int(match.group("vlan_id")),
                    "vlan_name": match.group("vlan_name"),
                    "vlan_type": match.group("vlan_type"),
                    "tagged_ports": tagged_ports,
                    "untagged_ports": untagged_ports
                }]

        fdb = self.scripts.get_mac_address_table()

        interfaces = []
        for p in ports:
            ifname = p['port']
            i = {
                "name": ifname,
                "type": "physical",
                "admin_status": p['admin_state'],
                "oper_status": p['status'],
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": p['admin_state'],
                    "oper_status": p['status'],
                    # "ifindex": 1,
                    "is_bridge": True
                }]
            }
            desc = p['desc']
            if desc != '' and desc != 'null':
                i.update({"description": desc})
                i['subinterfaces'][0].update({"description": desc})
            tagged_vlans = []
            for v in vlans:
                if p['port'] in v['tagged_ports']:
                    tagged_vlans += [v['vlan_id']]
                if p['port'] in v['untagged_ports']:
                    i['subinterfaces'][0]["untagged_vlan"] = v['vlan_id']
            if len(tagged_vlans) != 0:
                i['subinterfaces'][0]['tagged_vlans'] = tagged_vlans
            if lldp_enable and ifname in lldp:
                i["enabled_protocols"] += ["LLDP"]
            interfaces += [i]

        ipif = self.cli("show ipif")
        for match in self.rx_ipif1.finditer(ipif):
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            oper_status = re.match(self.rx_link_up, o_status) is not None
            i = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": match.group("ifname"),
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "is_ipv4": True,
                    "enabled_afi": ["IPv4"]
                }]
            }
            desc = "System interface"
            if desc is not None and desc != '':
                desc = desc.strip()
                i.update({"description": desc})
                i['subinterfaces'][0].update({"description": desc})
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            vlan_name = match.group("vlan_name")
            for v in vlans:
                if vlan_name == v['vlan_name']:
                    vlan_id = v['vlan_id']
                    i['subinterfaces'][0].update({"vlan_ids": [vlan_id]})
                    for f in fdb:
                        if 'CPU' in f['interfaces'] \
                        and vlan_id == f['vlan_id']:
                            i.update({"mac": f['mac']})
                            i['subinterfaces'][0].update({"mac": f['mac']})
                            break
                    break
            interfaces += [i]
        return [{"interfaces": interfaces}]
