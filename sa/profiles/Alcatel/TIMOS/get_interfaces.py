# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_interfaces
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces

class Script(NOCScript):
    TIMEOUT = 850
    name = "Alcatel.TIMOS.get_interfaces"
    implements = [IGetInterfaces]

    @staticmethod
    def fix_protocols(protocols):
        """
        :rtype : list
        """
        proto = []
        if 'None' in protocols:
            return []
        if 'OSPFv2' in protocols:
            proto += ["OSPF"]
        if 'OSPFv3' in protocols:
            proto += ["OSPFv3"]
        return proto

    @staticmethod
    def fix_status(status):
        return "up" in status.lower()

    @staticmethod
    def fix_ip_addr(ipaddr_section):
        """
        :rtype : dict
        """
        result = {
            'ipv4_addresses': [],
            'ipv6_addresses': [],
            'enabled_afi': [],
        }
        re_ipaddr = re.compile(r"""(IPv6\sAddr|IP\sAddr/mask)\s.*?:\s
                                   (?P<ipaddress>.+?)(\s|$)""",
                               re.VERBOSE | re.MULTILINE | re.DOTALL)
        if "Unnumbered If" in ipaddr_section:
            return result
        for line in ipaddr_section.splitlines():
            match_obj = re.search(re_ipaddr, line)
            if match_obj:
                afi = match_obj.group(1)
                ip = match_obj.group(2)
                if afi == 'IP Addr/mask' and 'Not' not in ip:
                    result['ipv4_addresses'] += [ip]
                elif afi == 'IPv6 Addr':
                    result['ipv6_addresses'] += [ip]
        if result['ipv4_addresses']:
            result['enabled_afi'] += ['IPv4']
        if result['ipv6_addresses']:
            result['enabled_afi'] += ['IPv6']
        return result

    def parse_interfaces(self, data):
        re_int = re.compile(r'-{79}\nInterface\n-{79}', re.MULTILINE)
        re_int_desc_vprn = re.compile(r"""
            If\sName\s*?:\s(?P<name>.*?)\n
            .*?
            Admin\sState\s*?:\s(?P<admin_status>.*?)\s+?
            Oper\s\(v4/v6\)\s*?:\s(?P<oper_status>.*?)\n
            (Down\sReason\sCode\s:\s.*?\n)*
            Protocols\s*?:\s(?P<protocols>.*?)\n
            (?P<ipaddr_section>(IP\sAddr/mask|IPv6\sAddr).*?)-{79}\n
            Details\n
            -{79}\n
            Description\s*?:\s(?P<description>.*?)\n
            .*?
            (SAP\sId|Port\sId|SDP\sId)\s+?:\s(?P<subinterfaces>.+?)\n
            .*?
            MAC\sAddress\s*?:\s(?P<mac>.*?)\s
            .*?
            IP\sOper\sMTU\s*?:\s(?P<mtu>.*?)\s
            .*?""", re.VERBOSE | re.MULTILINE | re.DOTALL)

        re_int_desc_subs = re.compile(r"""
            ^If\sName\s*?:\s(?P<name>.*?)\n
            .*?
            Admin\sState\s*?:\s(?P<admin_status>.*?)\s+?
            Oper\s\(v4/v6\)\s*?:\s(?P<oper_status>.*?)\n
            (Down\sReason\sCode\s:\s.*?\n)*
            Protocols\s*?:\s(?P<protocols>.*?)\n
            (?P<ipaddr_section>(IP\sAddr/mask|IPv6\sAddr|Unnumbered\sIf).*?)
            -{79}\n
            Details\n
            -{79}\n
            Description\s*?:\s(?P<description>.*?)\n
            """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        re_int_desc_group = re.compile(r"""
            ^If\sName\s*?:\s(?P<name>.*?)\n
            Sub\sIf\sName\s*?:\s(?P<ip_unnumbered_subinterface>.+?)\s+?\n
            .*?
            Admin\sState\s*?:\s(?P<admin_status>.*?)\s+?
            Oper\s\(v4/v6\)\s*?:\s(?P<oper_status>.*?)\n
            (Down\sReason\sCode\s:\s.*?\n)*
            Protocols\s*?:\s(?P<protocols>.*?)\n-{79}\n
            Details\n
            -{79}\n
            Description\s*?:\s(?P<description>.*?)\n
            .*?
            Srrp\sEn\sRtng\s*?:\s(?P<srrp>.*?)\s
            .*?
            MAC\sAddress\s*?:\s(?P<mac>.*?)\s
            .*?
            IP\sOper\sMTU\s*?:\s(?P<mtu>.*?)\s
            .*?
        """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        ifaces = re.split(re_int, data)
        result = []
        iftypeVPRN = ': VPRN'
        iftypeNetwork = ': Network'
        iftypeSubsc = ': VPRN Sub'
        iftypeGroup = ': VPRN Grp'
        iftypeRed = ': VPRN Red'

        for iface in ifaces[1:]:
            my_dict = {}
            if iftypeGroup in iface:
                match_obj = re.search(re_int_desc_group, iface)
                if match_obj:
                    my_dict = match_obj.groupdict()
                    my_dict['type'] = 'other'
                    my_dict['subinterfaces'] = []

            elif iftypeSubsc in iface:
                match_obj = re.search(re_int_desc_subs, iface)
                my_dict = match_obj.groupdict()
                my_dict['subinterfaces'] = [{}]
                my_dict['type'] = 'loopback'
                my_sub = {
                    'oper_status': my_dict['oper_status'],
                    'admin_status': my_dict['admin_status'],
                    'name': my_dict['name'],
                }
                if 'enabled_afi' in my_dict:
                    my_sub['enabled_afi'] = my_dict['enabled_afi']
                    my_dict.pop('enabled_afi')
                if 'ipv4_addresses' in my_dict:
                    my_sub['ipv4_addresses'] = my_dict['ipv4_addresses']
                    my_dict.pop('ipv4_addresses')
                if 'ipv6_addresses' in my_dict:
                    my_sub['ipv6_addresses'] = my_dict['ipv6_addresses']
                    my_dict.pop('ipv6_addresses')

                my_dict['subinterfaces'][0].update(my_sub)

            elif iftypeRed in iface:
                match_obj = re.search(re_int_desc_vprn, iface)
                my_dict = match_obj.groupdict()
                if 'subinterfaces' in my_dict:
                    my_dict['subinterfaces'] = [
                        {
                            'name': my_dict['subinterfaces'],
                            'type': 'tunnel'
                        }
                    ]
                my_dict['type'] = 'tunnel'

            elif iftypeNetwork in iface or iftypeVPRN in iface:
                match_obj = re.search(re_int_desc_vprn, iface)
                if match_obj:
                    my_dict = match_obj.groupdict()
                    if 'subinterfaces' in my_dict:
                        if my_dict['subinterfaces'].startswith('sdp'):
                            my_dict['type'] = 'tunnel'
                        elif my_dict['subinterfaces'].startswith('loopback'):
                            my_dict['type'] = 'loopback'
                        if my_dict['subinterfaces'].startswith('lag-'):
                            vlans = my_dict['subinterfaces'].split(":")[1]
                            if "." in vlans and "*" not in vlans:
                                up_tag, down_tag = vlans.split(".")

                                my_dict['vlan_ids'] = [int(up_tag), int(down_tag)]
                            elif "*" in vlans:
                                my_dict['vlan_ids'] = []
                            else:
                                my_dict['vlan_ids'] = [int(vlans)]

                        my_dict['subinterfaces'] = [
                            {
                                'name': my_dict['name']
                            }
                        ]
                else:
                    print iface
            else:
                continue
            if my_dict['description'] == '(Not Specified)':
                my_dict.pop('description')

            my_dict['protocols'] = self.fix_protocols(my_dict['protocols'])
            if 'srrp' in my_dict:
                my_dict['protocols'] += ['SRRP']
                my_dict.pop('srrp')

            my_dict['oper_status'] = self.fix_status(my_dict['oper_status'])
            my_dict['admin_status'] = self.fix_status(my_dict['admin_status'])
            if 'ipaddr_section' in my_dict:
                my_dict.update(self.fix_ip_addr(my_dict['ipaddr_section']))
                my_dict.pop('ipaddr_section')

            if 'subinterfaces' in my_dict:
                if type(my_dict['subinterfaces']) != list and \
                                type(my_dict['subinterfaces']) != dict:
                    my_dict['subinterfaces'] = [my_dict['subinterfaces']]
                if len(my_dict['subinterfaces']) == 1:
                    my_sub = {
                        'oper_status': my_dict['oper_status'],
                        'admin_status': my_dict['admin_status'],
                    }
                    if 'enabled_afi' in my_dict:
                        my_sub['enabled_afi'] = my_dict['enabled_afi']
                        my_dict.pop('enabled_afi')
                    if 'ipv4_addresses' in my_dict:
                        my_sub['ipv4_addresses'] = my_dict['ipv4_addresses']
                        my_dict.pop('ipv4_addresses')
                    if 'ipv6_addresses' in my_dict:
                        my_sub['ipv6_addresses'] = my_dict['ipv6_addresses']
                        my_dict.pop('ipv6_addresses')
                    if 'vlan_ids' in my_dict:
                        my_sub['vlan_ids'] = my_dict['vlan_ids']
                        my_dict.pop('vlan_ids')
                    my_dict['subinterfaces'][0].update(my_sub)

            if 'type' not in my_dict:
                my_dict['type'] = 'unknown'

            result.append(my_dict)
        return result

    @staticmethod
    def fix_fi_type(fitype):
        if fitype == "VPRN":
            fitype = "ip"
        elif fitype == "VPLS":
            fitype = "bridge"
        else:
            fitype = "Unsupported"
        return fitype


    def fix_vpls_saps(self, sap_section):
        result = {'interfaces': []}
        re_saps = re.compile(r"""
                    sap:(?P<interface>.+?):
                    (?P<uptag>(\d+?|\*))\.
                    (?P<downtag>(\d+?|\*))\s+
                    (?P<sap_type>.+?)\s+
                    (?P<admin_mtu>.+?)\s+
                    (?P<mtu>.+?)\s+
                    (?P<admin_status>.+?)\s+
                    (?P<oper_status>.+)""",
                             re.MULTILINE | re.DOTALL | re.VERBOSE)
        for line in sap_section.splitlines():
            match_obj = re.match(re_saps, line)
            if match_obj:
                raw_sap = match_obj.groupdict()
                sap = {
                    'name': raw_sap['interface'],
                    'subinterfaces': [{
                        'enabled_afi': ['BRIDGE'],
                        'name': str(raw_sap['interface'] + ":" + raw_sap['uptag'] + "." + raw_sap['downtag']),
                        'oper_status': self.fix_status(raw_sap['oper_status']),
                        'admin_status': self.fix_status(raw_sap['admin_status']),
                        'mtu': raw_sap['mtu'],
                        'vlan_ids': [raw_sap['uptag'], raw_sap['downtag']],
                    }]
                }
                if "*" in sap['subinterfaces'][0]['name']:
                    sap['subinterfaces'][0].pop('vlan_ids')
                if 'lag' in sap['name']:
                    sap['type'] = 'aggregated'
                else:
                    sap['type'] = 'physical'

                result['interfaces'] += [sap]

        return result

    def get_vpls(self, vpls_id):
        result = {
            'forwarding_instance': vpls_id,
            'type': 'VPLS'
        }
        re_vpls = re.compile(r"""
                Service\sId\s+:\s(?P<id>.+?)\s
                .*?
                Name\s+?:\s(?P<forwarding_instance>.+?)\n
                .+?
                Admin\sState\s+?:\s(?P<admin_status>.+?)\s
                .+?
                Oper\sState\s+?:\s(?P<oper_status>.+?)\n
                MTU\s+?:\s(?P<mtu>.+?)\s
                .+?
                Identifier.+?-{79}\n(?P<sap_section>.+?)={79}
        """, re.MULTILINE | re.DOTALL | re.VERBOSE)
        vpls = self.cli('show service id %s base' % vpls_id)
        match_obj = re.search(re_vpls, vpls)
        if match_obj:
            result = match_obj.groupdict()

            result['oper_status'] = self.fix_status(result['oper_status'])
            result['admin_status'] = self.fix_status(result['admin_status'])

            result['type'] = 'bridge'

            if result['forwarding_instance'] == '(Not Specified)':
                result['forwarding_instance'] = result['id']
            if result['sap_section']:
                result.update(self.fix_vpls_saps(result['sap_section']))
                result.pop('sap_section')
            else:
                result['interfaces'] = {
                    'type': 'unknown',
                    'subinterfaces': {'name': 'empty_vpls'},
                }

        return result


    def get_forwarding_instance(self):
        forwarding_instance = re.compile(
            r'^(?P<forwarding_instance>\d+)\s+(?P<type>\S+)\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)',
            re.MULTILINE)
        rd = re.compile(r'^Route Dist.\s+:\s(?P<rd>.+?)\s', re.MULTILINE)

        result = []
        o = self.cli("show service service-using")
        for line in o.splitlines():
            mo1 = re.search(forwarding_instance, line)
            if mo1:
                fi = mo1.groupdict()
                fi['type'] = self.fix_fi_type(fi['type'])
                fi['oper_status'] = self.fix_status(fi['oper_status'])
                fi['admin_status'] = self.fix_status(fi['admin_status'])

                if fi['type'] == 'ip' or fi['type'] == 'VRF':
                    r = self.cli('show service id %s base | match invert-match "sap:"' %
                                 fi["forwarding_instance"])
                    mo2 = re.search(rd, r)
                    fi["rd"] = mo2.group('rd')
                    if fi["rd"] == 'None':
                        fi.pop('rd')
                    if fi["forwarding_instance"] != "333100":
                        intf = self.cli('show router %s interface detail' % fi["forwarding_instance"])
                        fi['interfaces'] = self.parse_interfaces(intf)
                    if fi["forwarding_instance"] in ["100", "120"]:
                        fi["forwarding_instance"] = "default"
                    else:
                        fi['interfaces'] = []
                elif fi["type"] == 'bridge':
                    fi.update(self.get_vpls(fi['forwarding_instance']))
                    fi.pop('id')
                elif fi["type"] == "Unsupported":
                    continue
                result.append(fi)

        return result

    def get_managment_router(self):
        re_cards_detail = re.compile(r"""
            -{79}\n
            (?P<name>[A-B])\s+?sfm\d*-\d*\s+
            (?P<admin_status>.*?)\s+
            (?P<oper_status>.*?/.*?)\s
            .+?
            Base\sMAC\saddress\s*?:\s(?P<mac>.*?)\n
        """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        fi = {'forwarding_instance': 'management', 'type': 'ip', 'interfaces': []}
        card_detail = self.cli('show card detail')
        cards = re.findall(re_cards_detail, card_detail)

        for card in cards:
            sub_iface = self.cli('show router "management" interface detail')
            fi['interfaces'].append({
                'name': "/".join([card[0], "1"]),
                'admin_status': self.fix_status(card[1]),
                'oper_status': self.fix_status(card[2]),
                'protocols': [],
                'mac': card[3],
                'type': 'physical',
                'subinterfaces': self.parse_interfaces(sub_iface),
            })

        return fi

    def get_base_router(self):
        re_port_info = re.compile("""
            ^(?P<name>\d+/\d+/\d+)\s+
            (?P<admin_status>\S*)\s+
            (?P<bad_stat>\S*)\s+
            (?P<oper_status>\S*)\s+
            (?P<mtu>\d*)\s+
            (?P<oper_mtu>\d*)\s+
            (?P<aggregated_interface>\d*)\s
            """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        re_port_detail_info = re.compile("""
            Description\s*?:\s(?P<description>.*?)\n
            Interface\s*?:\s(?P<name>\d*/\d*/\S*)\s*
            .*?
            Admin\sState\s*?:\s(?P<admin_status>.*?)\s
            .*?
            Oper\sState\s*?:\s(?P<oper_status>.*?)\s
            .*?
            MTU\s*?:\s(?P<mtu>.*?)\s
            .*?
            IfIndex\s*?:\s(?P<snmp_ifindex>\d*)\s
            .*?
            Configured\sAddress\s*?:\s(?P<mac>.*?)\s
        """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        re_lag_detail = re.compile("""
            Description\s*?:\s(?P<description>.+?)\n-{79}
            .*?
            Detail
            .*?
            Lag-id\s*?:\s(?P<name>.*?)\s
            .*?
            Adm\s*?:\s(?P<admin_status>.*?)\s
            Opr\s*?:\s(?P<oper_status>.*?)\s
            .*?
            Configured\sAddress\s*?:\s(?P<mac>.*?)\s
            .*?
            Lag-IfIndex\s+:\s(?P<snmp_ifindex>.*?)\s
            .*?
            LACP\s*?:\s(?P<protocols>.*?)\s
            """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        re_lag_split = re.compile(r"""
                -{79}\n
                (?P<lag>LAG\s\d+.+?)
                Port-id\s+Adm""", re.VERBOSE | re.MULTILINE | re.DOTALL)
        re_lag_subs = re.compile(r"""(?P<physname>.+?):
            (?P<sapname>.+?)\s+
            (?P<svcid>.+?)\s+
            (?P<igq>.+?)\s+
            (?P<ingfil>.+?)\s+
            (?P<eggq>.+?)\s+
            (?P<eggfil>.+?)\s+
            (?P<admin_status>.+?)\s+
            (?P<oper_status>.+?)\s+
            """, re.VERBOSE | re.MULTILINE | re.DOTALL)
        fi = {
            'forwarding_instance': 'base',
            'type': 'ip',
            'interfaces': []
        }

        port_info = self.cli('show port')

        for line in port_info.splitlines():
            match = re.search(re_port_info, line)
            if match:
                port_detail = self.cli('show port %s detail' % match.group('name'))
                match_detail = re.search(re_port_detail_info, port_detail)
                my_dict = match.groupdict()
                my_dict.update(match_detail.groupdict())
                if 'aggregated_interface' in my_dict:
                    my_dict['aggregated_interface'] = "-".join(["lag", my_dict['aggregated_interface']])
                my_dict['type'] = 'physical'
                my_dict['subinterfaces'] = []
                my_dict.pop('bad_stat')
                fi['interfaces'].append(my_dict)

        lag_info = self.cli('show lag detail')

        lags = re.split(re_lag_split, lag_info)

        for lag in lags[1:]:
            match = re.search(re_lag_detail, lag)
            if match:
                my_dict = match.groupdict()
                my_dict['type'] = 'aggregated'
                if my_dict['name']:
                    my_dict['name'] = "-".join(['lag', my_dict['name']])
                my_dict['subinterfaces'] = []
                saps = self.cli('show service sap-using sap %s | match invert-match [' % my_dict['name'])
                for sapline in saps.splitlines():
                    sap = re.match(re_lag_subs, sapline)
                    if sap:
                        if sap.group('physname'):
                            my_dict['subinterfaces'].append({
                                'name': ":".join([sap.group('physname'), sap.group('sapname')]),
                                'admin_status': self.fix_status(sap.group('admin_status')),
                                'oper_status': self.fix_status(sap.group('admin_status')),
                            })
                my_dict['oper_status'] = self.fix_status(my_dict['oper_status'])
                my_dict['admin_status'] = self.fix_status(my_dict['admin_status'])
                if my_dict['protocols'] == 'Enabled':
                    my_dict['protocols'] = ['LACP']
                else:
                    my_dict['protocols'] = []
                fi['interfaces'].append(my_dict)

        return fi

    def execute(self):
        result = []
        fi = self.get_forwarding_instance()
        for forw_instance in fi:
            result.append(forw_instance)

        fi = self.get_managment_router()
        result.append(fi)
        fi = self.get_base_router()
        result.append(fi)

        return result