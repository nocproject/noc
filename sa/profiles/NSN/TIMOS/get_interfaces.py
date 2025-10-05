# ----------------------------------------------------------------------
#  NSN.TIMOS.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List, Dict, Any
import enum

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.validators import is_int, is_ipv6, is_vlan


class IfType(enum.Enum):
    vprn = ": VPRN"
    network = ": Network"
    subsc = ": VPRN Sub"
    group = ": VPRN Grp"
    red = ": VPRN Red"
    ies = ": IES"


class Script(BaseScript):
    name = "NSN.TIMOS.get_interfaces"
    interface = IGetInterfaces

    re_int = re.compile(r"-{79}\nInterface\n-{79}", re.MULTILINE)
    re_int_desc_vprn = re.compile(
        r"""
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
        .*?""",
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_int_desc_subs = re.compile(
        r"""
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
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_int_desc_group = re.compile(
        r"""
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
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_iface = re.compile(r"^(?P<iface>\d+/\d+/\d+|lag-\d+)")
    re_ipaddr = re.compile(
        r"""
        (IPv6\sAddr|IP\sAddr/mask)\s.*?:\s(?P<ipaddress>.+?)(\s|$)
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_saps = re.compile(
        r"""
        sap:(?P<interface>.+?):
        (?P<uptag>(\d+?|\*))\.
        (?P<downtag>(\d+?|\*))\s+
        (?P<sap_type>.+?)\s+
        (?P<admin_mtu>.+?)\s+
        (?P<mtu>.+?)\s+
        (?P<admin_status>.+?)\s+
        (?P<oper_status>.+)
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )
    re_vpls = re.compile(
        r"""
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
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )
    re_forwarding_instance = re.compile(
        r"^(?P<forwarding_instance>\d+)\s+(?P<type>\S+)\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)",
        re.MULTILINE,
    )
    re_rd = re.compile(r"^Route Dist.\s+:\s(?P<rd>.+?)\s", re.MULTILINE)
    re_cards_detail = re.compile(
        r"""
        -{79}\n
        (?P<name>[A-B])\s+?sfm\d*-\d*\s+
        (?P<admin_status>.*?)\s+
        (?P<oper_status>.*?/.*?)\s
        .+?
        Base\sMAC\saddress\s*?:\s(?P<mac>.*?)\n
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_port_info = re.compile(
        r"""
        ^(?P<name>((esat-|)\d+/\d+/(c\d+|\d+)(/\d+|/u\d+|)|\w+\/\d+))\s+
        (?P<admin_status>\S*)\s+
        (?P<bad_stat>\S*)\s+
        (?:Link\s)?(?P<oper_status>\S*)\s+
        (?P<mtu>\d*)\s+(?P<oper_mtu>\d*)\s+
        (?P<aggregated_interface>\d*)\s
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_port_detail_info = re.compile(
        r"""
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
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_port_detail_info_sr = re.compile(
        r"""
        Description\s*?:\s(?P<description>.*?)\n
        Interface\s*?:\s(?P<name>((esat-|)\d+/\d+/(c\d+|\d+)(/\d+|/u\d+|)|\w+\/\d+))\s*[\S\s]+
        Admin\sState\s*?:\s(?P<admin_status>.*?)\s.*?
        Oper\sState\s*?:\s(?P<oper_status>.*?)\s.*?
        IfIndex\s*?:\s(?P<snmp_ifindex>\d*)\s.*?
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_port_detail_info_sar = re.compile(
        r"""
        Description\s*?:\s(?P<description>.*?)\n
        Interface\s*?:\s(?P<name>\S+)\s+
        Port\sIfIndex\s+:\s(?P<snmp_ifindex>\d+)\n
        Admin\sStatus\s*?:\s(?P<admin_status>\S+)\s.*?
        Oper\sStatus\s*?:\s(?P<oper_status>\S+)\s.*?
        .*?
        Hardware\sAddress\s*?:\s(?P<mac>\S+)
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_lag_detail = re.compile(
        r"""
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
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_lag_split = re.compile(
        r"""
        -{79}\n
        (?P<lag>LAG\s\d+.+?|Lag\-id\s*:\s*\d+.+?)
        Port-id\s+Adm
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    re_lag_subs = re.compile(
        r"""(?P<physname>.+?):
        (?P<sapname>.+?)\s+
        (?P<svcid>.+?)\s+
        (?P<igq>.+?)\s+
        (?P<ingfil>.+?)\s+
        (?P<eggq>.+?)\s+
        (?P<eggfil>.+?)\s+
        (?P<admin_status>.+?)\s+
        (?P<oper_status>.+?)\s+
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )

    @staticmethod
    def fix_protocols(protocols: str) -> List[str]:
        """
        :rtype : list
        """
        proto = []
        if "None" in protocols:
            return []
        if "OSPFv2" in protocols:
            proto += ["OSPF"]
        if "OSPFv3" in protocols:
            proto += ["OSPFv3"]
        if "PIM" in protocols:
            proto += ["PIM"]
        if "IGMP" in protocols:
            proto += ["IGMP"]
        if "RSVP" in protocols:
            proto += ["RSVP"]
        return proto

    @staticmethod
    def fix_status(status: str) -> bool:
        return "up" in status.lower()

    @staticmethod
    def fix_fi_type(fitype: str) -> str:
        fitype = fitype.lower()
        if fitype == "vprn":
            fitype = "ip"
        elif fitype == "vpls":
            fitype = "bridge"
        else:
            fitype = "Unsupported"
        return fitype

    def fix_ip_addr(self, ipaddr_section: str) -> Dict[str, List[str]]:
        """
        :rtype : dict
        """
        result = {"ipv4_addresses": [], "ipv6_addresses": [], "enabled_afi": []}
        if "Unnumbered If" in ipaddr_section:
            return result
        for line in ipaddr_section.splitlines():
            match_obj = self.re_ipaddr.search(line)
            if match_obj:
                afi = match_obj.group(1)
                ip = match_obj.group(2)
                if afi == "IP Addr/mask" and "Not" not in ip:
                    result["ipv4_addresses"] += [ip]
                elif afi == "IPv6 Addr" and is_ipv6(ip):
                    result["ipv6_addresses"] += [ip]
        if result["ipv4_addresses"]:
            result["enabled_afi"] += ["IPv4"]
        if result["ipv6_addresses"]:
            result["enabled_afi"] += ["IPv6"]
        return result

    def parse_interfaces(self, data: str, c_interfaces=None):
        interfaces: Dict[str, Dict[str, Any]] = c_interfaces or {}
        r = self.re_int.split(data)
        for block in r[1:]:
            parent_iface = ""
            iface: Dict[str, Any] = {}
            if IfType.group.value in block:
                match = self.re_int_desc_group.search(block)
                if match:
                    iface = match.groupdict()
                    if "mac" in iface and iface["mac"] == "":
                        del iface["mac"]
                    iface["type"] = "other"
                    iface["subinterfaces"] = []
            elif IfType.subsc.value in block:
                match = self.re_int_desc_subs.search(block)
                iface = match.groupdict()
                if "mac" in iface and iface["mac"] == "":
                    del iface["mac"]
                iface["subinterfaces"] = []
                iface["type"] = "loopback"
                sub = {
                    "name": iface["name"],
                }
                if "enabled_afi" in iface:
                    sub["enabled_afi"] = iface["enabled_afi"]
                    iface.pop("enabled_afi")
                if "ipv4_addresses" in iface:
                    sub["ipv4_addresses"] = iface["ipv4_addresses"]
                    iface.pop("ipv4_addresses")
                if "ipv6_addresses" in iface:
                    sub["ipv6_addresses"] = iface["ipv6_addresses"]
                    iface.pop("ipv6_addresses")
                iface["subinterfaces"].append(sub)
            elif IfType.red.value in block:
                match = self.re_int_desc_vprn.search(block)
                iface = match.groupdict()
                if "mac" in iface and iface["mac"] == "":
                    del iface["mac"]
                iface["type"] = "tunnel"
                if "subinterfaces" in iface:
                    iface["subinterfaces"] = [{"name": iface["subinterfaces"], "type": "tunnel"}]
            elif (
                IfType.network.value in block
                or IfType.vprn.value in block
                or IfType.ies.value in block
            ):
                match = self.re_int_desc_vprn.search(block)
                if not match:
                    continue
                iface = match.groupdict()
                if "mac" in iface and iface["mac"] == "":
                    del iface["mac"]
                if "subinterfaces" in iface:
                    if iface["subinterfaces"].startswith("sdp"):
                        iface["type"] = "tunnel"
                    elif iface["subinterfaces"].startswith("loopback"):
                        iface["type"] = "loopback"
                    match = self.re_iface.search(iface["subinterfaces"])
                    if match:
                        parent_iface = match.group("iface")
                        if ":" in iface["subinterfaces"]:
                            vlans = iface["subinterfaces"].split(":")[1]
                            if "." in vlans and "*" not in vlans:
                                up_tag, down_tag = vlans.split(".")
                                if is_vlan(down_tag):
                                    iface["vlan_ids"] = [int(up_tag), int(down_tag)]
                                else:
                                    iface["vlan_ids"] = [int(up_tag)]
                            elif "*" in vlans:
                                iface["vlan_ids"] = []
                            elif int(vlans) == 0:
                                iface["vlan_ids"] = []
                            else:
                                iface["vlan_ids"] = [int(vlans)]
                    iface["subinterfaces"] = [{"name": iface["name"]}]
            else:
                continue

            if iface["description"] == "(Not Specified)":
                iface.pop("description")
            proto = iface["protocols"]
            iface["protocols"] = self.fix_protocols(iface["protocols"])
            if "srrp" in iface:
                iface["protocols"] += ["SRRP"]
                iface.pop("srrp")
            iface["oper_status"] = self.fix_status(iface["oper_status"])
            iface["admin_status"] = self.fix_status(iface["admin_status"])
            if "ipaddr_section" in iface:
                iface.update(self.fix_ip_addr(iface["ipaddr_section"]))
                iface.pop("ipaddr_section")
            if "subinterfaces" in iface:
                if not isinstance(iface["subinterfaces"], (list, dict)):
                    iface["subinterfaces"] = [iface["subinterfaces"]]
                if len(iface["subinterfaces"]) == 1:
                    sub = {
                        "oper_status": iface["oper_status"],
                        "admin_status": iface["admin_status"],
                        "protocols": iface["protocols"],
                        "enabled_afi": [],
                    }
                    iface.pop("protocols")
                    if "enabled_afi" in iface:
                        sub["enabled_afi"] = iface.pop("enabled_afi")
                    if "ipv4_addresses" in iface:
                        sub["ipv4_addresses"] = iface.pop("ipv4_addresses")
                    if "ipv6_addresses" in iface:
                        sub["ipv6_addresses"] = iface.pop("ipv6_addresses")
                    if "vlan_ids" in iface:
                        sub["vlan_ids"] = iface.pop("vlan_ids")
                    if "MPLS" in proto:
                        sub["enabled_afi"] += ["MPLS"]
                    if "mac" in iface and iface["mac"]:
                        sub["mac"] = iface["mac"]
                    if "mtu" in iface:
                        sub["mtu"] = iface.pop("mtu")
                    if not iface["subinterfaces"]:
                        iface["subinterfaces"] = [sub]
                    else:
                        iface["subinterfaces"][0].update(sub)
                    if c_interfaces and parent_iface in c_interfaces:
                        sub["name"] = iface["name"]
                        interfaces[parent_iface]["subinterfaces"].append(sub)
                        continue
            if "type" not in iface:
                iface["type"] = "unknown"
            interfaces[iface["name"]] = iface
        return interfaces

    def parse_vpls_saps(self, sap_section: str) -> Dict[str, Any]:
        result = {}
        for line in sap_section.splitlines():
            match = self.re_saps.match(line)
            if not match:
                continue
            raw_sap = match.groupdict()
            sap = {
                "name": raw_sap["interface"],
                "subinterfaces": [
                    {
                        "enabled_afi": ["BRIDGE"],
                        "name": str(
                            raw_sap["interface"] + ":" + raw_sap["uptag"] + "." + raw_sap["downtag"]
                        ),
                        "oper_status": self.fix_status(raw_sap["oper_status"]),
                        "admin_status": self.fix_status(raw_sap["admin_status"]),
                        "mtu": raw_sap["mtu"],
                        "vlan_ids": [raw_sap["uptag"], raw_sap["downtag"]],
                    }
                ],
            }
            if "*" in sap["subinterfaces"][0]["name"]:
                sap["subinterfaces"][0].pop("vlan_ids")
            if "lag" in sap["name"]:
                sap["type"] = "aggregated"
            else:
                sap["type"] = "physical"
            result[raw_sap["interface"]] = sap
        return result

    def get_managment_router(self):
        interfaces: Dict[str, Dict[str, Any]] = {}
        card_detail = self.cli("show card detail")
        cards = self.re_cards_detail.findall(card_detail)

        for card in cards:
            sub_iface = self.cli('show router "management" interface detail')
            ifname = f"{card[0]}/1"
            interfaces[ifname] = {
                "name": "/".join([card[0], "1"]),
                "admin_status": self.fix_status(card[1]),
                "oper_status": self.fix_status(card[2]),
                "protocols": [],
                "type": "physical",
                "subinterfaces": self.parse_interfaces(sub_iface),
            }
            if card[3]:
                interfaces[ifname]["mac"] = card[3]
        return list(interfaces.values())

    def get_base_router(self) -> Dict[str, Any]:
        """
        Getting Router physical ifaces.
        :return:
        """
        interfaces: Dict[str, Dict[str, Any]] = {}
        port_info = self.cli("show port")
        for line in port_info.splitlines():
            match = self.re_port_info.search(line)
            if match:
                port_detail = self.cli("show port %s detail" % match.group("name"))
                match_detail = self.re_port_detail_info.search(port_detail)
                if not match_detail:
                    match_detail = self.re_port_detail_info_sr.search(port_detail)
                    if not match_detail:
                        match_detail = self.re_port_detail_info_sar.search(port_detail)
                iface: Dict[str, Any] = match.groupdict()
                iface.update(match_detail.groupdict())
                if "aggregated_interface" in iface:
                    if is_int(iface["aggregated_interface"]):
                        iface["aggregated_interface"] = f"lag-{iface['aggregated_interface']}"
                    else:
                        del iface["aggregated_interface"]
                iface["type"] = "physical"
                if "mac" in iface and iface["mac"] == "":
                    del iface["mac"]
                iface["subinterfaces"] = []
                iface.pop("bad_stat")
                iface["description"] = iface["description"].replace("\n", "")
                interfaces[iface["name"]] = iface
        # LAG
        lag_info = self.cli("show lag detail")
        lags = self.re_lag_split.split(lag_info)
        for lag in lags[1:]:
            match = self.re_lag_detail.search(lag)
            if match:
                iface = match.groupdict()
                iface["type"] = "aggregated"
                if iface["name"]:
                    iface["name"] = f"lag-{iface['name']}"
                if "mac" in iface and iface["mac"] == "":
                    del iface["mac"]
                iface["subinterfaces"] = []
                # QinQ
                # saps = self.cli(
                #     f'show service sap-using sap {iface["name"]} | match invert-match ['
                # )
                # for sapline in saps.splitlines():
                #     sap = self.re_lag_subs.match(sapline)
                #     if sap and sap.group("physname"):
                #         vlans = sap.group("sapname")
                #         sub = {
                #             "name": f'{sap.group("physname")}:{vlans}',
                #             "admin_status": self.fix_status(sap.group("admin_status")),
                #             "oper_status": self.fix_status(sap.group("admin_status")),
                #         }
                #         if "." in vlans and "*" not in vlans:
                #             up_tag, down_tag = vlans.split(".")
                #             if is_vlan(down_tag):
                #                 sub["vlan_ids"] = [int(up_tag), int(down_tag)]
                #             else:
                #                 sub["vlan_ids"] = [int(up_tag)]
                #         elif "*" in vlans:
                #             sub["vlan_ids"] = []
                #         elif int(vlans) == 0:
                #             sub["vlan_ids"] = []
                #         else:
                #             sub["vlan_ids"] = [int(vlans)]
                #         iface["subinterfaces"].append(sub)
                iface["oper_status"] = self.fix_status(iface["oper_status"])
                iface["admin_status"] = self.fix_status(iface["admin_status"])
                if iface["protocols"].lower() == "enabled":
                    iface["protocols"] = ["LACP"]
                else:
                    iface["protocols"] = []
                iface["description"] = iface["description"].replace("\n", "")
                interfaces[iface["name"]] = iface
        v = self.cli('show router "Base" interface detail')
        self.parse_interfaces(v, interfaces)

        return interfaces

    def execute_cli(self, **kwargs):
        result = []
        # Mgmt Router Ifaces
        mgmt_ifaces = self.get_managment_router()
        if mgmt_ifaces:
            result += [
                {"forwarding_instance": "management", "type": "ip", "interfaces": mgmt_ifaces}
            ]
        # Mgmt Router Ifaces
        base_ifaces = self.get_base_router()
        # Forwarding Instance
        v = self.cli("show service service-using")
        for line in v.splitlines():
            """
            ===============================================================================
            ServiceId    Type      Adm  Opr  CustomerId Service Name
            -------------------------------------------------------------------------------
            2            IES       Up   Down 1
            3            VPLS      Up   Up   1          SVLAN_3
            """
            match = self.re_forwarding_instance.search(line)
            if not match:
                continue
            fi: Dict[str, Any] = match.groupdict()
            fi["type"] = self.fix_fi_type(fi["type"])
            # fi["oper_status"] = self.fix_status(fi["oper_status"])
            # fi["admin_status"] = self.fix_status(fi["admin_status"])
            if fi["type"] == "ip" or fi["type"] == "vrf":
                r = self.cli(
                    f'show service id {fi["forwarding_instance"]} base | match invert-match "sap:"'
                )
                mo2 = self.re_rd.search(r)
                fi["rd"] = mo2.group("rd")
                if fi["rd"] == "None":
                    fi.pop("rd")
                fi["interfaces"] = []
                v = self.cli(f"show router {fi['forwarding_instance']} interface detail")
                ifaces = self.parse_interfaces(v)
                for iface in ifaces:
                    if iface not in base_ifaces:
                        fi["interfaces"].append(ifaces[iface])
                        continue
                    for si in ifaces[iface]["subinterfaces"]:
                        fi["interfaces"].append(
                            {
                                "name": si["name"],
                                "type": "other",
                                "enabled_protocols": [],
                                "subinterfaces": [si],
                            }
                        )
            elif fi["type"] == "bridge":
                v = self.cli(f"show service id {fi['forwarding_instance']} base")
                match = self.re_vpls.search(v)
                if not match:
                    fi["type"] = "vpls"
                    continue
                vpls: Dict[str, Any] = match.groupdict()
                fi.update(vpls)
                vpls["type"] = "bridge"
                fi["oper_status"] = self.fix_status(fi["oper_status"])
                fi["admin_status"] = self.fix_status(fi["admin_status"])
                if vpls["forwarding_instance"] == "(Not Specified)":
                    fi["forwarding_instance"] = vpls["id"]
                fi["interfaces"] = []
                if vpls["sap_section"]:
                    sap_ifaces = self.parse_vpls_saps(fi.pop("sap_section"))
                    for iface in sap_ifaces:
                        if iface not in base_ifaces:
                            fi["interfaces"].append(sap_ifaces[iface])
                            continue
                        for si in sap_ifaces[iface]["subinterfaces"]:
                            fi["interfaces"].append(
                                {
                                    "name": si["name"],
                                    "type": "other",
                                    "enabled_protocols": [],
                                    "subinterfaces": [si],
                                }
                            )
                    # fi.update(self.fix_vpls_saps(fi.pop("sap_section")))
                else:
                    fi["interfaces"].append(
                        {
                            "type": "unknown",
                            "subinterfaces": {"name": "empty_vpls"},
                        }
                    )
                fi.pop("id")
            elif fi["type"] == "Unsupported":
                continue
            result.append(fi)
        if base_ifaces:
            result += [
                {
                    "forwarding_instance": "default",
                    "type": "ip",
                    "interfaces": list(base_ifaces.values()),
                }
            ]
        return result
