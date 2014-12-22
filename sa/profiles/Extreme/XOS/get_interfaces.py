# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    """
    Extreme.XOS.get_interfaces
    """
    name = "Extreme.XOS.get_interfaces"
    implements = [IGetInterfaces]

    #System MAC:       00:04:96:83:5B:6F
    rx_system_mac = re.compile(r'System MAC:\s+(?P<mac>\S+)$')

    #Config    Current    Agg       Ld Share    Ld Share  Agg   Link    Link Up
    #Master    Master     Control   Algorithm   Group     Mbr   State   Transitions
    #==============================================================================
    #     1      1        LACP      L3_L4       1          Y      A        2
    # --or--
    #   6:1    6:1        LACP      L3_L4       6:1        Y      A        0
    rx_sharing_master = re.compile(
        r"^\s+(?P<name>\d+(:\d+)?)\s+\d+(:\d+)?\s+(?P<protocol>\S+)\s+\S+\s+"
        r"\d+(:\d+)?\s+\S\s+\S\s+\d+.*$")

    #                               L3_L4       2          Y      A        2
    # --or--
    #                               L3_L4       6:2        Y      A        0
    rx_sharing_slave = re.compile(
        r'^\s+\S+\s+(?P<name>\d+(:\d+)?)\s+\S\s+\S\s+\d+.*$')

    # Port:   4:4
    # Port:   4
    rx_port_name = re.compile(
        r'Port:\s+(?P<name>\d+(:\d+)?)(\((?P<display_string>\S+)\):)?')

    #Admin state:    Enabled with  40G full-duplex
    rx_port_admin_status = re.compile(r'^\s+Admin state:\s+(?P<state>.*)$')

    # Link State:     Not present
    # Link State:     Active, 40Gbps, full-duplex
    # Link State:     Ready
    rx_port_oper_status = re.compile(r'^\s+Link State:\s+(?P<state>.*)$')

    # VLAN Interface with name v931-Radiosystem-World created by user
    rx_vlan_name = re.compile(
        r'^(VLAN|VMAN)\s+Interface.*\s+with\s+name\s+(?P<name>.+?)\s+created')

    #        Virtual router: VR-Default
    rx_vlan_vrf = re.compile(r'^\s+Virtual\s+router:\s+(?P<name>\S+).*$')

    #        Primary IP    : 10.14.12.1/30
    rx_vlan_ipv4_address = re.compile(r'^\s+Primary\s+IP(\s+)?:\s+(?P<address>(\d+\.){3}\d+\/\d+).*$')

    #        Loopback:       Enabled
    rx_vlan_loopback_mode = re.compile(r'^\s+Loopback:\s+(?P<state>\S+).*$')

    #        Admin State:    Enabled         Tagging:Untagged (Internal tag 4059)
    # --or--
    #        Admin State:    Enabled         Tagging:        802.1Q Tag 131
    rx_vlan_admin_status = re.compile(r'^\s+Admin\sState:\s+(?P<state>\S+).*$')
    rx_vlan_tag = re.compile(r"^.*Tagging:\s+802.1Q\s+Tag\s+(?P<tag>\d+)\s*$")

    #           Tag:   *15(NNI_H3C-TRUNK),    *1g
    # --or--
    #        Tag:   *4:45(csw01-kiev@49),*6:46(mr01-kiev), *6:19g, *6:36g, *6:14g
    rx_vlan_tagged_ports = re.compile(r'^\s+Tag:\s+(?P<ports>.*$)')

    #           Untag:       9,     10
    rx_vlan_untagged_ports = re.compile(r'^\s+Untag:\s+(?P<ports>.*$)')

    #*32(FREENET-LVOV-QinQ)
    #*4:45(csw01-kiev@49)
    #*6:18(alc-leo1.kiev@3/26)
    #6:28(GOOLE-PEER)
    rx_vlan_port_name = re.compile(r'^[!*]?(?P<port>\d+(:\d+)?).*$')

    #VR-Default                    3            0    -opr--ORS46
    #VR-Ethernet                  13            0    --------U46
    rx_vrf = re.compile(r'^(?P<name>\S+)\s+\d+\s+\d+\s+(?P<flags>\S+).*$')

    def execute(self):
        def expand_interface_range(l):
            ports = []
            for p in l.split(","):
                p = p.strip()
                match = self.rx_vlan_port_name.match(p)
                if match:
                    ports.append(match.group('port'))
            return ports

        # get mac address
        mac = None
        v = self.cli('show switch')
        for l in v.splitlines():
            match = self.rx_system_mac.match(l)
            if match:
                mac = match.group('mac')

        # process sharings
        ports_and_sharings = {}  # sharing -> master
        sharing_members = {}
        v = self.cli('show sharing')
        current_master = None
        for l in v.splitlines():
            match = self.rx_sharing_master.match(l)
            if match:
                current_master_name = match.group('name')
                current_master = {
                    'name': current_master_name,
                    'admin_status': True,
                    'oper_status': True,
                    'tagged_vlans': [],
                    'type': 'aggregated',
                    'enabled_afi': ['BRIDGE'],
                }
                ports_and_sharings[current_master_name] = current_master
                sharing_members[current_master_name] = {
                    'master': current_master_name,
                }
                continue
            match = self.rx_sharing_slave.match(l)
            if match:
                sharing_members[match.group('name')] = {
                    'master': current_master_name,
                }
                continue

        # process ports
        v = self.cli('show ports information detail')
        #v = v.replace(",\n", ",")
        for l in v.splitlines():
            match = self.rx_port_name.match(l)
            if match:
                current_port_name = match.group('name')
                if current_port_name in sharing_members:
                    sharing_master_name = sharing_members[current_port_name]['master']
                    if sharing_master_name == current_port_name:
                        current_port_name = '{0} - Sharing {0} master'.format(current_port_name)
                    else:
                        current_port_name = '{0} - Sharing {1} slave'.format(current_port_name, sharing_master_name)
                    current_port = {
                        'name': current_port_name,
                        'aggregated_interface': sharing_master_name,
                        'enabled_protocols': [],
                        'type': 'physical',
                    }
                else:
                    current_port = {
                        'name': current_port_name,
                        'tagged_vlans': [],
                        'type': 'physical',
                        'enabled_afi': ['BRIDGE'],
                    }
                ports_and_sharings[current_port_name] = current_port
                description = match.group('display_string')
                if description:
                    ports_and_sharings[current_port_name]['description'] = description
                continue
            match = self.rx_port_admin_status.match(l)
            if match:
                if 'Enabled' in match.group('state'):
                    ports_and_sharings[current_port_name]['admin_status'] = True
                else:
                    ports_and_sharings[current_port_name]['admin_status'] = False
                continue
            match = self.rx_port_oper_status.match(l)
            if match:
                if 'Active' in match.group('state'):
                    ports_and_sharings[current_port_name]['oper_status'] = True
                else:
                    ports_and_sharings[current_port_name]['oper_status'] = False
                continue

        #process vlans
        vlans = {}
        v = self.cli('show vlan detail')
        v += self.cli('show vman detail')
        v = v.replace(',\n', ',')
        for l in v.splitlines():
            match = self.rx_vlan_name.match(l)
            if match:
                name = match.group('name')
                current_vlan = {
                    'name': name,
                    'vlan_id': None,
                    'admin_status': None,
                    'oper_status': None,
                    'enabled_afi': [],
                    'ipv4_addresses': [],
                    'ipv6_addresses': [],
                    'type': 'SVI',
                    'vrf': None,
                }
                vlans[name] = current_vlan
                continue
            match = self.rx_vlan_vrf.match(l)
            if match:
                vrf_name = match.group('name')
                current_vlan['vrf'] = match.group('name')
            match = self.rx_vlan_ipv4_address.match(l)
            #TODO: Add secondaries and ipv6
            if match:
                if not 'IPv4' in current_vlan['enabled_afi']:
                    current_vlan['enabled_afi'].append('IPv4')
                current_vlan['ipv4_addresses'].append(match.group('address'))
            match = self.rx_vlan_loopback_mode.match(l)
            if match:
                if 'Enabled' in match.group('state'):
                    current_vlan['type'] = 'loopback'
                continue
            match = self.rx_vlan_admin_status.match(l)
            if match:
                if 'Enabled' in match.group('state'):
                    current_vlan['admin_status'] = True
                    current_vlan['oper_status'] = True
                else:
                    current_vlan['admin_status'] = False
                    current_vlan['oper_status'] = False
            match = self.rx_vlan_tag.match(l)
            if match:
                current_vlan['vlan_id'] = int(match.group('tag'))
                continue
            match = self.rx_vlan_tagged_ports.match(l)
            if match:
                for p in expand_interface_range(match.group('ports')):
                    ports_and_sharings[p]['tagged_vlans'].append(current_vlan['vlan_id'])
                continue
            match = self.rx_vlan_untagged_ports.match(l)
            if match:
                for p in expand_interface_range(match.group('ports')):
                    ports_and_sharings[p]['untagged_vlan'] = current_vlan['vlan_id']
                continue

        # VRF
        vrfs = {}
        v = self.cli('show virtual-router')
        for l in v.splitlines():
            match = self.rx_vrf.match(l)
            if match:
                vrf_name = match.group('name')
                current_vrf = {
                    'name': vrf_name,
                }
                vrfs[vrf_name] = current_vrf

        # generate return data
        # Process VRFs
        ret = {}
        for e in vrfs.values():
            vrf_name = e['name']
            out_vrf = {
                'forwarding_instance': vrf_name,
                'interfaces': [],
                'type': 'ip',
            }
            ret[vrf_name] = out_vrf
        default_vrf = ret['VR-Default']
        default_vrf['forwarding_instance'] = 'default'  # fix default instance name

        # Ports & Sharings
        for e in ports_and_sharings.values():
            name = e['name']
            admin_status = e['admin_status']
            oper_status = e['oper_status']
            aggregated_interface = e.get('aggregated_interface')
            if_type = e['type']
            description = e.get('description')
            enabled_afi = e.get('enabled_afi')
            out_subif = {
                'name': name,
                'admin_status': admin_status,
                'oper_status': oper_status,
                'mac': mac,
            }
            if enabled_afi:
                out_subif['enabled_afi'] = enabled_afi
            out_if = {
                'name': name,
                'admin_status': admin_status,
                'oper_status': oper_status,
                'mac': mac,
                'type': if_type,
                'subinterfaces': [out_subif]
            }
            if description:
                out_subif['description'] = description
                out_if['description'] = description
            if aggregated_interface:
                out_if['aggregated_interface'] = aggregated_interface
            default_vrf['interfaces'].append(out_if)

        # SVIs
        for e in vlans.values():
            enabled_afi = e['enabled_afi']
            name = e['name']
            vlan_id = e['vlan_id']
            vrf = e['vrf']
            admin_status = e['admin_status']
            oper_status = e['oper_status']
            ipv4_addresses = e['ipv4_addresses']
            ipv6_addresses = e['ipv6_addresses']
            if_type = e['type']
            out_subif = {
                'name': name,
                'admin_status': admin_status,
                'oper_status': oper_status,
                'enabled_afi': enabled_afi,
                'mac': mac,
            }
            if vlan_id:
                out_subif['vlan_ids'] = [vlan_id]
            if ipv4_addresses:
                out_subif['ipv4_addresses'] = ipv4_addresses
            if ipv6_addresses:
                out_subif['ipv6_addresses'] = ipv6_addresses
            out_if = {
                'name': name,
                'admin_status': admin_status,
                'oper_status': oper_status,
                'mac': mac,
                'type': if_type,
                'subinterfaces': [out_subif]
            }
            ret[vrf]['interfaces'].append(out_if)
        return ret.values()
