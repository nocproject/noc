# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
import time
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4
from noc.sa.profiles.DLink.DxS import DxS_L2
from noc.sa.profiles.DLink.DxS import DGS3620


class Script(NOCScript):
    name = "DLink.DxS.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 300

    rx_ipif1 = re.compile(r"Interface Name\s+:\s+(?P<ifname>.+?)\s*\n"
    r"IP Address\s+:\s+(?P<ip_address>\S+)\s+\(\S+\)\s*\n"
    r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
    r"Admin. State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
    r"Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n"
    r"Member Ports\s+:\s*\S*\s*\n"
    r"(IPv6 Link-Local Address\s+:\s+\S+\s*\n)?"
    r"(IPv6 Global Unicast Address\s+:\s+(?P<ipv6_address>\S+)\s*\n)?"
    r"(DHCP Option12 State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(DHCP Option12 Host Name\s+:\s*\S*\s*\n)?"
    r"(Description\s+:\s*(?P<desc>\S*?)\s*\n)?",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_ipif2 = re.compile(r"IP Interface\s+:\s+(?P<ifname>.+?)\s*\n"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S*)\s*\n"
    r"Interface Admin.? State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
    r"(DHCPv6 Client State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n)?"
    r"(IPv4 Address\s+:\s+(?P<ipv4_address>\S+)\s+\(\S+\)\s*\n)?"
    r"(IPv4 Address\s+:\s+(?P<ipv4_addr_pri>\S+)\s+\(\S+\)\s+Primary\s*\n)?"
    r"(Proxy ARP\s+:\s+(?:Enabled|Disabled)\s+\(Local : \S+\s*\)\s*\n)?"
    r"(IPv4 State\s+:\s+(?P<is_ipv4>Enabled|Disabled)\s*\n)?"
    r"(IPv6 State\s+:\s+(?P<is_ipv6>Enabled|Disabled)\s*\n)?"
    r"(IP Directed Broadcast\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(IPv6 Link-Local Address\s+:\s+\S+\s*\n)?"
    r"(IPv6 Global Unicast Address\s+:\s+(?P<ipv6_address>\S+) \(\S+\)\s*\n)?"
    r"(IP MTU\s+:\s+(?P<mtu>\d+)\s+\n)?",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    # Work only on DES-1210-XX/ME/BX
    rx_ipif3 = re.compile(r"IP Interface\s+:\s+(?P<ifname>.+?)\s*\n"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S*)\s*\n"
    r"Interface Admin.? State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
    r"(IPv4 Address\s+:\s+(?P<ipv4_address>\S+)\s+\(\S+\)\s*\n)?"
    r"(IPv6 Link-Local Address\s+:\s+\S+\s*\n)?"
    r"(IPv6 Global Unicast Address\s+:\s+(?P<ipv6_address>\S+) \(\S+\)\s*\n)?"
    r"(DHCPv6 Client State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(IPv4 State\s+:\s+(?P<is_ipv4>Enabled|Disabled)\s*\n)?"
    r"(IPv6 State\s+:\s+(?P<is_ipv6>Enabled|Disabled)\s*\n)?",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_ipmgmt = re.compile(r"IP Interface\s+:\s+(?P<ifname>mgmt_ipif)\s*\n"
    r"Status\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
    r"IP Address\s+:\s+(?P<ip_address>\S+)\s*\n"
    r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n"
    r"(Gateway\s+:\s+\S+\s*\n)?"
    r"Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_link_up = re.compile(r"Link\s*UP", re.IGNORECASE)

    rx_rip_gs = re.compile(r"RIP Global State : Enabled")
    rx_ospf_gs = re.compile(
        r"OSPF Router ID : \S+ (\(.+\))?\s*\nState\s+: Enabled")
    rx_ospfv3_gs = re.compile(
        r"OSPFv3 Router ID : \S+(\(.+\))?\s*\nState\s+: Enabled")
    rx_lldp_gs = re.compile(r"LLDP Status\s+: Enabled")
    rx_ctp_gs = re.compile(r"(LBD )?Status\s+: Enabled")
    rx_pim_gs = re.compile(r"PIM Global State\s+: Enabled")
    rx_gvrp_gs = re.compile(r"Global GVRP\s+: Enabled")
    rx_stp_gs = re.compile(r"STP Status\s+: Enabled")

    rx_rip = re.compile(r"(?P<ipif>\S+)\s+\S+\s+(?:Disabled|Enabled)\s+"
    r"(?:Disabled|Enabled)\s+(?:Disabled|Enabled)\s+"
    r"(?P<state>Enabled)\s*")

    rx_ospf = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\S+\s+(?P<state>Enabled)\s+"
    r"Link (?:Up|DOWN)\s+\d+\d*", re.IGNORECASE)
    rx_ospfv3 = re.compile(r"(?P<ipif>\S+)\s+\S+\s+(?P<state>Enabled)\s+"
    r"Link (?:Up|DOWN)\s+\d+", re.IGNORECASE)

    rx_lldp = re.compile(r"Port ID\s+:\s+(?P<ipif>\S+)\s*\n"
    r"\-+\s*\nAdmin Status\s+: (?:TX_and_RX|RX_Only|TX_Only)")
    rx_lldp1 = re.compile(r"Port ID\s+:\s+(?P<ipif>\S+)\s*\n"
    r"\-+\s*\nPort ID Subtype\s+: MAC Address\s*\n"
    r"Port ID\s+: (?P<mac>\S+)")

    rx_pd = re.compile(r"Port\s+:\s+(?P<ipif>\S+)\s*\n"
    r"\-+\s*\nPort Status\s+: Link (?:Up|Down)\s*\n"
    r"Description\s+:\s*(?P<desc>\S*?)\s*\n"
    r"HardWare Type\s+:\s*.+\s*\n"
    r"MAC Address\s+:\s*(?P<mac>\S+)\s*\n")

    rx_udld = re.compile(r"(?P<ipif>\S+)\s+Enabled\s+\S+\s+\S+\s+\S+\s+\d+")

    rx_ctp = re.compile(r"^(?P<ipif>\S+)\s+(?P<state>Enabled|Disabled)\s+\S+",
        re.MULTILINE)

    rx_pim = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\S+\s+\d+\s+\d+\s+\S+\s+"
    r"(?P<state>Enabled)\s+")

    rx_igmp = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+"
    r"\d+\s+(?P<state>Enabled)\s+")

    rx_gvrp = re.compile(r"^ (?P<ipif>\d+)\s+\d+\s+(?P<state>Enabled)")

    rx_stp = re.compile(r"Port Index\s+: (?P<ipif>\d+([:/]\d+)?)\s+.+?Port STP (: )?(?P<state>Enabled|Disabled)")
    rx_stp1 = re.compile(r"Port Index\s+: (?P<ipif>\d+)\s*\n"
        r"Connection\s+: Link (?:Up|Down)\s*\n"
        r"State : (?P<state>Yes|Enabled|No|Disabled)")

    def parse_ctp(self, s):
        match = self.rx_ctp.search(s)
        if match:
            key = match.group("ipif")
            state = match.group("state")
            obj = {"port": key, "state": state}
            return key, obj, s[match.end():]
        else:
            return None

    def parse_stp(self, s):
        match = self.rx_stp.search(s)
        if match:
            key = match.group("ipif")
            state = match.group("state")
            obj = {"port": key, "state": state}
            return key, obj, s[match.end():]
        else:
            match = self.rx_stp1.search(s)
            if match:
                key = match.group("ipif")
                state = match.group("state")
                obj = {"port": key, "state": state}
                return key, obj, s[match.end():]
        return None

    def execute(self):
        if self.match_version(DxS_L2):
            L2_Switch = True
        else:
            L2_Switch = False

            rip = []
            try:
                c = self.cli("show rip")
            except self.CLISyntaxError:
                c = ""
            rip_enable = self.rx_rip_gs.search(c) is not None
            if rip_enable:
                for match in self.rx_rip.finditer(c):
                    rip += [match.group("ipif")]

            ospf = []
            try:
                c = self.cli("show ospf")
            except self.CLISyntaxError:
                c = ""
            ospf_enable = self.rx_ospf_gs.search(c) is not None
            if ospf_enable:
                for match in self.rx_ospf.finditer(c):
                    ospf += [match.group("ipif")]

            ospfv3 = []
            try:
                c = self.cli("show ospfv3")
            except self.CLISyntaxError:
                c = ""
            ospfv3_enable = self.rx_ospfv3_gs.search(c) is not None
            if ospfv3_enable:
                for match in self.rx_ospfv3.finditer(c):
                    ospf += [match.group("ipif")]

            pim = []
            try:
                c = self.cli("show pim")
            except self.CLISyntaxError:
                c = ""
            pim_enable = self.rx_pim_gs.search(c) is not None
            if pim_enable:
                for match in self.rx_pim.finditer(c):
                    pim += [match.group("ipif")]

            igmp = []
            try:
                c = self.cli("show igmp")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_igmp.finditer(c):
                igmp += [match.group("ipif")]


        lldp = []
        macs = []
        try:
            c = self.cli("show lldp")
            lldp_enable = self.rx_lldp_gs.search(c) is not None
            try:
                c = self.cli("show lldp local_ports")
                for match in self.rx_lldp1.finditer(c):
                    macs += [{
                        "ipif": match.group("ipif"),
                        "mac":  match.group("mac")
                    }]
            except self.CLISyntaxError:
                pass
        except self.CLISyntaxError:
            lldp_enable = False
        if lldp_enable:
            try:
                c = self.cli("show lldp ports")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_lldp.finditer(c):
                lldp += [match.group("ipif")]

        if self.match_version(DGS3620, version__gte="2.60.16"):
            try:
                c = self.cli("show ports details")
                for match in self.rx_pd.finditer(c):
                    macs += [{
                        "ipif": match.group("ipif"),
                        "mac":  match.group("mac")
                    }]
            except self.CLISyntaxError:
                pass

        udld = []
        try:
            c = self.cli("show duld ports")
        except self.CLISyntaxError:
            c = ""
        for match in self.rx_udld.finditer(c):
            udld += [match.group("ipif")]

        ctp = []
        try:
            c = self.cli("show loopdetect")
        except self.CLISyntaxError:
            c = ""
        ctp_enable = self.rx_ctp_gs.search(c) is not None
        if ctp_enable:
            c = []
            try:
                c = self.cli_object_stream(
                "show loopdetect ports all", parser=self.parse_ctp,
                cmd_next="n", cmd_stop="q")
            except self.CLISyntaxError:
                c = []
            if c == []:
                self.reset_cli_queue()
                c = self.cli_object_stream(
                "show loopdetect ports", parser=self.parse_ctp,
                cmd_next="n", cmd_stop="q")
            for i in c:
                if i['state'] == 'Enabled':
                    ctp += [i['port']]

        gvrp = []
        try:
            c = self.cli("show gvrp")
        except self.CLISyntaxError:
            c = ""
        gvrp_enable = self.rx_gvrp_gs.search(c) is not None
        if gvrp_enable:
            try:
                c1 = self.cli("show port_vlan")
            except self.CLISyntaxError:
                c1 = c
            for match in self.rx_gvrp.finditer(c1):
                gvrp += [match.group("ipif")]

        stp = []
        try:
            c = self.cli("show stp")
        except self.CLISyntaxError:
            c = ""
        stp_enable = self.rx_stp_gs.search(c) is not None
        if stp_enable:
            c = self.cli_object_stream(
            "show stp ports", parser=self.parse_stp,
            cmd_next="n", cmd_stop="q")
            for i in c:
                if i['state'] in ['Enabled', 'Yes']:
                    stp += [i['port']]

        ports = self.profile.get_ports(self)
        vlans = self.profile.get_vlans(self)
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
                    "enabled_afi": ['BRIDGE']
                }]
            }
            desc = p['desc']
            if desc != '' and desc != 'null':
                i.update({"description": desc})
                i['subinterfaces'][0].update({"description": desc})
            for m in macs:
                if p['port'] == m['ipif']:
                    i['mac'] = m['mac']
                    i['subinterfaces'][0]["mac"] = m['mac']
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
            if ctp_enable and ifname in ctp:
                i["enabled_protocols"] += ["CTP"]
            if ifname in udld:
                i["enabled_protocols"] += ["UDLD"]
            if gvrp_enable and ifname in gvrp:
                i["enabled_protocols"] += ["GVRP"]
            if stp_enable and ifname in stp:
                i["enabled_protocols"] += ["STP"]
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
                    "enabled_afi": ["IPv4"]
                }]
            }
            desc = match.group("desc")
            if desc is not None and desc != '':
                desc = desc.strip()
                i.update({"description": desc})
                i['subinterfaces'][0].update({"description": desc})
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            ipv6_address = match.group("ipv6_address")
            if ipv6_address is not None:
                i['subinterfaces'][0]["ipv6_addresses"] = [ipv6_address]
                i['subinterfaces'][0]["enabled_afi"] += ["IPv6"]
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

        for match in self.rx_ipif2.finditer(ipif):
            enabled_afi = []
            enabled_protocols = []
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            if o_status is not None:
                oper_status = re.match(self.rx_link_up, o_status) is not None
            else:
                oper_status = admin_status
            ifname = match.group("ifname")
            i = {
                "name": ifname,
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "enabled_afi": []
                }]
            }
            mtu = match.group("mtu")
            if mtu is not None:
                i['subinterfaces'][0]["mtu"] = int(mtu)
            # TODO: Parse secondary IPv4 address and IPv6 address
            ipv4_addresses = []
            ipv4_address = match.group("ipv4_address")
            if ipv4_address is not None:
                ipv4_addresses += [ipv4_address]
                if not "IPv4" in enabled_afi:
                    enabled_afi += ["IPv4"]
            ipv4_addr_pri = match.group("ipv4_addr_pri")
            if ipv4_addr_pri is not None:
                ipv4_addresses += [ipv4_addr_pri]
                if not "IPv4" in enabled_afi:
                    enabled_afi += ["IPv4"]
            if ipv4_address is not None \
            or ipv4_addr_pri is not None:
                i['subinterfaces'][0].update({
                    "ipv4_addresses": ipv4_addresses
                })
            ipv6_address = match.group("ipv6_address")
            if ipv6_address is not None:
                i['subinterfaces'][0]["ipv6_addresses"] = [ipv6_address]
                enabled_afi += ["IPv6"]
            i['subinterfaces'][0].update({"enabled_afi": enabled_afi})
            vlan_name = match.group("vlan_name")
            # Found illegal stuff in DES-1210-28/ME/B2
            # In this rotten device System interface always in vlan 1
            if not vlan_name:
                vlan_name = "default"
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
            if not L2_Switch:
                if rip_enable and ifname in rip:
                    enabled_protocols += ["RIP"]
                if ospf_enable and ifname in ospf:
                    enabled_protocols += ["OSPF"]
                if ospfv3_enable and ifname in ospfv3:
                    enabled_protocols += ["OSPFv3"]
                if pim_enable and ifname in pim:
                    enabled_protocols += ["PIM"]
                if ifname in igmp:
                    enabled_protocols += ["IGMP"]
                i['subinterfaces'][0]["enabled_protocols"] = enabled_protocols
            interfaces += [i]
        if self.match_version(DGS3620):
            match = self.rx_ipmgmt.search(ipif)
            if match:
                admin_status = match.group("admin_state") == "Enabled"
                o_status = match.group("oper_status")
                oper_status = re.match(self.rx_link_up, o_status) is not None
                i = {
                    "name": match.group("ifname"),
                    "type": "management",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "subinterfaces": [{
                        "name": match.group("ifname"),
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["IPv4"]
                    }]
                }
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
                interfaces += [i]

        return [{"interfaces": interfaces}]
