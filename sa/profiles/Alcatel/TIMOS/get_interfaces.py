# ----------------------------------------------------------------------
#  Alcatel.TIMOS.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.validators import is_int, is_ipv6, is_vlan


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_interfaces"
    interface = IGetInterfaces

    re_int = re.compile(r"-{79}\nInterface\n-{79}", re.MULTILINE)
    re_int_desc_vprn = re.compile(
        r"""
        If\sName\s*?:\s(?P<name>.*?)\n
        .*?
        Admin\sState\s*?:\s(?P<admin_status>.*?)\s+?
        Oper\s\(v4/v6\)\s*?:\s(?P<oper_status>.*?)\n
        (Down\sReason\s(?:Code|V4|V6)\s+:\s.*?\n)*
        Protocols\s*?:\s(?P<protocols>.*?)\n
        (?P<ipaddr_section>(IP\sAddr/mask|IPv6\sAddr).*?)?-{79}\n
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
        ^(?P<name>\d+/\d+/\d+)\s+
        (?P<admin_status>\S*)\s+
        (?P<bad_stat>\S*)\s+
        (?:Link\s)?(?P<oper_status>\S*)\s+
        (?P<mtu>\d*)\s+
        (?P<oper_mtu>\d*)\s+
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
        (?P<lag>LAG\s\d+.+?|Lag-id\s:\s\d+\sLag-name\s:\s\S+.+?)
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
    def fix_protocols(protocols):
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
    def fix_status(status):
        return "up" in status.lower()

    def fix_ip_addr(self, ipaddr_section):
        """
        :rtype : dict
        """
        result = {"ipv4_addresses": [], "ipv6_addresses": [], "enabled_afi": []}
        if not ipaddr_section:
            return result
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

    def parse_interfaces(self, data, vrf):
        ifaces = self.re_int.split(data)
        result = []
        iftypeVPRN = ": VPRN"
        iftypeNetwork = ": Network"
        iftypeSubsc = ": VPRN Sub"
        iftypeGroup = ": VPRN Grp"
        iftypeRed = ": VPRN Red"
        iftypeIES = ": IES"

        for iface in ifaces[1:]:
            parent_iface = ""
            my_dict = {}
            if iftypeGroup in iface:
                match_obj = self.re_int_desc_group.search(iface)
                if match_obj:
                    my_dict = match_obj.groupdict()
                    if "mac" in my_dict and not my_dict["mac"]:
                        my_dict.pop("mac")
                    if my_dict["name"].startswith("Vlan"):
                        my_dict["type"] = "SVI"
                    else:
                        my_dict["type"] = "other"
                    my_dict["subinterfaces"] = []
            elif iftypeSubsc in iface:
                match_obj = self.re_int_desc_subs.search(iface)
                if "mac" in my_dict and not my_dict["mac"]:
                    my_dict.pop("mac")
                my_dict = match_obj.groupdict()
                my_dict["subinterfaces"] = [{}]
                my_dict["type"] = "loopback"
                my_sub = {
                    "oper_status": my_dict["oper_status"],
                    "admin_status": my_dict["admin_status"],
                    "name": my_dict["name"],
                }
                if "enabled_afi" in my_dict:
                    my_sub["enabled_afi"] = my_dict["enabled_afi"]
                    my_dict.pop("enabled_afi")
                if "ipv4_addresses" in my_dict:
                    my_sub["ipv4_addresses"] = my_dict["ipv4_addresses"]
                    my_dict.pop("ipv4_addresses")
                if "ipv6_addresses" in my_dict:
                    my_sub["ipv6_addresses"] = my_dict["ipv6_addresses"]
                    my_dict.pop("ipv6_addresses")
                my_dict["subinterfaces"][0].update(my_sub)
            elif iftypeRed in iface:
                match_obj = self.re_int_desc_vprn.search(iface)
                my_dict = match_obj.groupdict()
                if "subinterfaces" in my_dict:
                    my_dict["subinterfaces"] = [
                        {"name": my_dict["subinterfaces"], "type": "tunnel"}
                    ]
                my_dict["type"] = "tunnel"
            elif iftypeNetwork in iface or iftypeVPRN in iface or iftypeIES in iface:
                match_obj = self.re_int_desc_vprn.search(iface)
                if match_obj:
                    my_dict = match_obj.groupdict()
                    if "mac" in my_dict and not my_dict["mac"]:
                        my_dict.pop("mac")
                    if "subinterfaces" in my_dict:
                        if my_dict["subinterfaces"].startswith("sdp"):
                            my_dict["type"] = "tunnel"
                        elif my_dict["subinterfaces"].startswith("loopback"):
                            my_dict["type"] = "loopback"
                        match = self.re_iface.search(my_dict["subinterfaces"])
                        if match:
                            parent_iface = match.group("iface")
                            if ":" in my_dict["subinterfaces"]:
                                my_dict["vlan_ids"] = []
                                vlans = my_dict["subinterfaces"].split(":")[1]
                                if is_vlan(vlans):
                                    my_dict["vlan_ids"] = [int(vlans)]
                                if "." in vlans and "*" not in vlans:
                                    up_tag, down_tag = vlans.split(".")
                                    if is_vlan(up_tag):
                                        my_dict["vlan_ids"] += [int(up_tag)]
                                    if is_vlan(down_tag):
                                        my_dict["vlan_ids"] += [int(down_tag)]
                        my_dict["subinterfaces"] = [{"name": my_dict["name"]}]
            else:
                continue
            if my_dict["description"] == "(Not Specified)":
                my_dict.pop("description")
            proto = my_dict["protocols"]
            my_dict["protocols"] = self.fix_protocols(my_dict["protocols"])
            if "srrp" in my_dict:
                my_dict["protocols"] += ["SRRP"]
                my_dict.pop("srrp")
            my_dict["oper_status"] = self.fix_status(my_dict["oper_status"])
            my_dict["admin_status"] = self.fix_status(my_dict["admin_status"])
            if "ipaddr_section" in my_dict:
                my_dict.update(self.fix_ip_addr(my_dict["ipaddr_section"]))
                my_dict.pop("ipaddr_section")
            if "subinterfaces" in my_dict:
                if not isinstance(my_dict["subinterfaces"], (list, dict)):
                    my_dict["subinterfaces"] = [my_dict["subinterfaces"]]
                if len(my_dict["subinterfaces"]) == 1:
                    my_sub = {
                        "oper_status": my_dict["oper_status"],
                        "admin_status": my_dict["admin_status"],
                        "protocols": my_dict["protocols"],
                    }
                    my_dict.pop("protocols")
                    if "enabled_afi" in my_dict:
                        my_sub["enabled_afi"] = my_dict["enabled_afi"]
                        my_dict.pop("enabled_afi")
                    if "ipv4_addresses" in my_dict:
                        my_sub["ipv4_addresses"] = my_dict["ipv4_addresses"]
                        my_dict.pop("ipv4_addresses")
                    if "ipv6_addresses" in my_dict:
                        my_sub["ipv6_addresses"] = my_dict["ipv6_addresses"]
                        my_dict.pop("ipv6_addresses")
                    if "vlan_ids" in my_dict:
                        my_sub["vlan_ids"] = my_dict["vlan_ids"]
                        my_dict.pop("vlan_ids")
                    if "MPLS" in proto:
                        if "enabled_afi" in my_sub:
                            my_sub["enabled_afi"] += ["MPLS"]
                        else:
                            my_sub["enabled_afi"] = ["MPLS"]
                    if "mac" in my_dict and my_dict["mac"]:
                        my_sub["mac"] = my_dict["mac"]
                    if "mtu" in my_dict:
                        my_sub["mtu"] = my_dict["mtu"]
                        my_dict.pop("mtu")
                    my_dict["subinterfaces"][0].update(my_sub)
                    if vrf:
                        found = False
                        for i in vrf:
                            if i["name"] == parent_iface:
                                my_sub["name"] = my_dict["name"]
                                i["subinterfaces"] += [my_sub]
                                found = True
                                break
                        if found:
                            continue
            if "type" not in my_dict:
                my_dict["type"] = "unknown"
            result += [my_dict]
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
        result = {"interfaces": []}
        for line in sap_section.splitlines():
            match_obj = self.re_saps.match(line)
            if match_obj:
                raw_sap = match_obj.groupdict()
                sap = {
                    "name": raw_sap["interface"],
                    "subinterfaces": [
                        {
                            "enabled_afi": ["BRIDGE"],
                            "name": str(
                                raw_sap["interface"]
                                + ":"
                                + raw_sap["uptag"]
                                + "."
                                + raw_sap["downtag"]
                            ),
                            "oper_status": self.fix_status(raw_sap["oper_status"]),
                            "admin_status": self.fix_status(raw_sap["admin_status"]),
                            "mtu": raw_sap["mtu"],
                            "vlan_ids": [raw_sap["uptag"]],
                        }
                    ],
                }
                if is_vlan(raw_sap["downtag"]):
                    sap["subinterfaces"][0]["vlan_ids"] += [int(raw_sap["downtag"])]
                if "*" in sap["subinterfaces"][0]["name"]:
                    sap["subinterfaces"][0].pop("vlan_ids")
                if "lag" in sap["name"]:
                    sap["type"] = "aggregated"
                else:
                    sap["type"] = "physical"
                result["interfaces"] += [sap]
        return result

    def get_vpls(self, vpls_id):
        result = {"forwarding_instance": vpls_id, "type": "VPLS"}
        vpls = self.cli("show service id %s base" % vpls_id)
        match_obj = self.re_vpls.search(vpls)
        if match_obj:
            result = match_obj.groupdict()

            result["oper_status"] = self.fix_status(result["oper_status"])
            result["admin_status"] = self.fix_status(result["admin_status"])

            result["type"] = "bridge"

            if result["forwarding_instance"] == "(Not Specified)":
                result["forwarding_instance"] = result["id"]
            if result["sap_section"]:
                result.update(self.fix_vpls_saps(result["sap_section"]))
                result.pop("sap_section")
            else:
                result["interfaces"] = {"type": "unknown", "subinterfaces": {"name": "empty_vpls"}}
        return result

    def get_forwarding_instance(self):
        result = []
        o = self.cli("show service service-using")
        for line in o.splitlines():
            mo1 = self.re_forwarding_instance.search(line)
            if mo1:
                fi = mo1.groupdict()
                fi["type"] = self.fix_fi_type(fi["type"])
                fi["oper_status"] = self.fix_status(fi["oper_status"])
                fi["admin_status"] = self.fix_status(fi["admin_status"])

                if fi["type"] == "ip" or fi["type"] == "VRF":
                    r = self.cli(
                        'show service id %s base | match invert-match "sap:"'
                        % fi["forwarding_instance"]
                    )
                    mo2 = self.re_rd.search(r)
                    fi["rd"] = mo2.group("rd")
                    if fi["rd"] == "None":
                        fi.pop("rd")
                    intf = self.cli("show router %s interface detail" % fi["forwarding_instance"])
                    fi["interfaces"] = self.parse_interfaces(intf, "")
                elif fi["type"] == "bridge":
                    fi.update(self.get_vpls(fi["forwarding_instance"]))
                    fi.pop("id")
                elif fi["type"] == "Unsupported":
                    continue
                result.append(fi)
        return result

    def get_managment_router(self):
        fi = {"forwarding_instance": "management", "type": "ip", "interfaces": []}
        card_detail = self.cli("show card detail")
        cards = self.re_cards_detail.findall(card_detail)

        for card in cards:
            sub_iface = self.cli('show router "management" interface detail')
            fi["interfaces"].append(
                {
                    "name": "/".join([card[0], "1"]),
                    "admin_status": self.fix_status(card[1]),
                    "oper_status": self.fix_status(card[2]),
                    "protocols": [],
                    "type": "physical",
                    "subinterfaces": self.parse_interfaces(sub_iface, ""),
                }
            )
            if card[3]:
                fi["interfaces"][-1]["mac"] = card[3]
        return fi

    def get_base_router(self):
        fi = {"forwarding_instance": "default", "type": "ip", "interfaces": []}

        port_info = self.cli("show port")

        for line in port_info.splitlines():
            match = self.re_port_info.search(line)
            if match:
                port_detail = self.cli("show port %s detail" % match.group("name"))
                match_detail = self.re_port_detail_info.search(port_detail)
                my_dict = match.groupdict()
                my_dict.update(match_detail.groupdict())
                if "aggregated_interface" in my_dict:
                    if is_int(my_dict["aggregated_interface"]):
                        my_dict["aggregated_interface"] = "-".join(
                            ["lag", my_dict["aggregated_interface"]]
                        )
                    else:
                        del my_dict["aggregated_interface"]
                my_dict["type"] = "physical"
                my_dict["subinterfaces"] = []
                my_dict.pop("bad_stat")
                my_dict["description"] = my_dict["description"].replace("\n", "")
                fi["interfaces"].append(my_dict)
        lag_info = self.cli("show lag detail")

        lags = self.re_lag_split.split(lag_info)

        for lag in lags[1:]:
            match = self.re_lag_detail.search(lag)
            if match:
                my_dict = match.groupdict()
                my_dict["type"] = "aggregated"
                if my_dict["name"]:
                    my_dict["name"] = "-".join(["lag", my_dict["name"]])
                my_dict["subinterfaces"] = []
                saps = self.cli(
                    "show service sap-using sap %s | match invert-match [" % my_dict["name"]
                )
                for sapline in saps.splitlines():
                    sap = self.re_lag_subs.match(sapline)
                    if sap:
                        if sap.group("physname"):
                            vlans = sap.group("sapname")
                            s = {
                                "name": ":".join([sap.group("physname"), vlans]),
                                "admin_status": self.fix_status(sap.group("admin_status")),
                                "oper_status": self.fix_status(sap.group("admin_status")),
                            }
                            if "." in vlans and "*" not in vlans:
                                up_tag, down_tag = vlans.split(".")
                                s["vlan_ids"] = [int(up_tag), int(down_tag)]
                            elif "*" in vlans:
                                s["vlan_ids"] = []
                            elif vlans != "0":
                                s["vlan_ids"] = [int(vlans)]
                            my_dict["subinterfaces"].append(s)
                my_dict["oper_status"] = self.fix_status(my_dict["oper_status"])
                my_dict["admin_status"] = self.fix_status(my_dict["admin_status"])
                if my_dict["protocols"].lower() == "enabled":
                    my_dict["protocols"] = ["LACP"]
                else:
                    my_dict["protocols"] = []
                my_dict["description"] = my_dict["description"].replace("\n", "")
                fi["interfaces"].append(my_dict)
        intf = self.cli('show router "Base" interface detail')
        fi["interfaces"] += self.parse_interfaces(intf, fi["interfaces"])

        return fi

    def execute_cli(self):
        result = []

        fi = self.get_forwarding_instance()
        for forw_instance in fi:
            result += [forw_instance]
        fi = self.get_managment_router()
        result += [fi]

        fi = self.get_base_router()
        result += [fi]

        return result
