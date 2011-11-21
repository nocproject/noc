# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.sa.interfaces import base
from noc.sa.script import Script as NOCScript
from noc.sa.profiles.Cisco.IOS import uBR


class Script(NOCScript):
    """
    Cisco.IOS.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """
    name = "Cisco.IOS.get_interfaces"
    implements = [IGetInterfaces]

    rx_sh_int = re.compile(r"^(?P<interface>.+?)\s+is(\sadministratively)?\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)\s(\((?:connected|notconnect)\))?\n\s+Hardware is (?P<hardw>[^\n]+)\n(\s+Description:\s(?P<desc>[^\n]+)\n)?(\s+Internet address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\n)?[^\n]+\n[^\n]+\n\s+Encapsulation\s+(?P<encaps>[^\n]+)",
                           re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(r"address\sis\s(?P<mac>\w{4}\.\w{4}\.\w{4})", re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(r"Internet address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})", re.MULTILINE | re.IGNORECASE)
    rx_sec_ip = re.compile(r"Secondary address (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})", re.MULTILINE | re.IGNORECASE)
    rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+(?P<status>active|suspend|act\/unsup)\s+(?P<ports>[\w\/\s\,\.]+)$", re.MULTILINE)
    rx_ospf = re.compile(r"^(?P<name>\S+)\s+\d", re.MULTILINE)
    rx_cisco_interface_name = re.compile(r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+)?)?([.:]\d+(\.\d+)?)?)$", re.IGNORECASE)

    types = {
           "Lo": 'loopback',   # Loopback
           "Et": 'physical',   # Ethernet
           "Fa": 'physical',   # FastEthernet
           "Gi": 'physical',   # GigabitEthernet
           "Te": 'physical',   # TenGigabitEthernet
           "Se": 'physical',   # Serial
           "M": 'management',
           "R": 'aggregated',
           "Tu": 'tunnel',
           "C": 'physical',
           "Vl": 'SVI',        # Vlan
           "Ca": 'physical',   # Cable
           "As": 'physical',   # Async
           "BV": 'aggregated', # BVI
           "Bu": 'aggregated', # Bundle
           "MF": 'aggregated', # Multilink Frame Relay
           "Gr": 'physical',   # Group-Async
           "Po": 'aggregated'  # Port-channel/Portgroup
           }

    def get_ospfint(self):
        try:
            v = self.cli("show ip ospf interface brief")
        except self.CLISyntaxError:
            return []
        ospfs = []
        for s in v.split("\n"):
            match = self.rx_ospf.search(s)
            if match:
                ospfs.append(match.group('name'))
        return ospfs

    def map_vlans_to_ports(self, data):
        pvm = {}
        for l in data.split('\n'):
            match = self.rx_vlan_line.search(l)
            if match:
                ports = match.group("ports")
                vlan_id = int(match.group("vlan_id"))
                for i in ports.split(', '):
                    if not i in pvm.keys():
                        pvm[i] = ['%s' % vlan_id]
                    else:
                        pvm[i] += '%s' % vlan_id
        return pvm

    ##
    ## Cisco uBR7100, uBR7200, uBR7200VXR, uBR10000 Series
    ##
    rx_vlan_ubr = re.compile(r"^\w{4}\.\w{4}\.\w{4}\s(?P<port>\S+)\s+(?P<vlan_id>\d{1,4})")

    def get_ubr_pvm(self):
        vlans = self.cli("show cable l2-vpn dot1q-vc-map")
        pvm = {}
        for l in vlans.split('\n'):
            match = self.rx_vlan_ubr.search(l)
            if match:
                    port = match.group("port")
                    vlan_id = int(match.group("vlan_id"))
                    if not port in pvm.keys():
                            pvm[port] = ['%s' % vlan_id]
                    else:
                            pvm[port] += ['%s' % vlan_id]
        return pvm

    def execute(self):
        # Get port-to-vlan mappings
        pvm = {}
        if self.match_version(uBR):
            # uBR series
            pvm = self.get_ubr_pvm()
        else:
            vlans = None
            for cmd in ("show vlan brief", "show vlan-switch brief"):
                try:
                    vlans = self.cli(cmd)
                except self.CLISyntaxError:
                    continue
            if vlans:
                pvm = self.map_vlans_to_ports(vlans)
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        interfaces = []
        subinterfaces = []
        # Get OSPF interfaces
        ospfs = self.get_ospfint()

        v = self.cli("show interface")
        for match in self.rx_sh_int.finditer(v):
            ifname = match.group('interface')
            if ifname[:2] in ['Vi', 'Tu', 'Di']:
                continue
            if ifname.find(':') > 0:
                inm = ifname.split(':')[0]
                if inm != interfaces[-1]['name']:
                    iface = {'name': inm, 'admin_status': True, 'oper_status': True, 'type': 'physical'}
                    interfaces.append(iface)
            a_stat = match.group('admin_status').lower() == "up"
            o_stat = match.group('oper_status').lower() == "up"
            hw = match.group('hardw')
            sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    }
            if 'alias' in match.groups():
                sub['description'] = match.group('alias')
            if match.group('desc'):
                sub["description"] = match.group('desc')
            matchmac = self.rx_mac.search(hw)
            if matchmac:
                sub['mac'] = matchmac.group('mac')
            if ifname in portchannel_members:
                iface["aggregated_interface"] = portchannel_members[ifname][0]
                iface["is_lacp"] = portchannel_members[ifname][1]

            #Static vlans
            if match.group('encaps'):
                encaps = match.group('encaps')
                if encaps[:6] == '802.1Q':
                    sub['vlan_ids'] = [encaps.split(',')[1].split()[2][:-1]]
            #vtp
            if ifname in pvm:
                sub['vlan_ids'] = pvm[ifname]

            if match.group('ip'):
                    ip = match.group('ip')
                    sub['ipv4_addresses'] = [base.IPv4PrefixParameter().clean(ip)]
                    sub['is_ipv4'] = True
            #Have to check for the secondary ip via 'show ip interface'
                    sh_ip = self.cli("show ip interface %s" % ifname)
                    for i in sh_ip.split('\n'):
                        matchsec = self.rx_sec_ip.search(i)
                        if matchsec:
                            ip = matchsec.group('ip')
                            sub['ipv4_addresses'] += [base.IPv4PrefixParameter().clean(ip)]

            matchifn = self.rx_cisco_interface_name.match(ifname)
            shotn = matchifn.group("type").capitalize() + matchifn.group("number")
            if shotn in ospfs:
                    sub['is_ospf'] = True
            phys = len(ifname.split('.')) + len(ifname.split(':'))
            if phys == 2:
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": self.types[ifname[:2]],
                    'subinterfaces': [sub]
                }
                if match.group('desc'):
                    iface["description"] = match.group('desc')
                if 'mac' in sub.keys():
                    iface['mac'] = sub['mac']
                if 'alias' in sub.keys():
                    iface['alias'] = sub['alias']
                # Set VLAN IDs for SVI
                if iface['type'] == "SVI":
                    sub["vlan_ids"] = [int(shotn[2:].strip())]
                interfaces += [iface]
            else:
                if 'subinterfaces' in interfaces[-1].keys():
                    interfaces[-1]['subinterfaces'].append(sub)
                else:
                    interfaces[-1]['subinterfaces'] = [sub]
        return [{"interfaces": interfaces}]
