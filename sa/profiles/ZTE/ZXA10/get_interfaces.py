# ---------------------------------------------------------------------
# ZTE.ZXA10.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces

# NOC modules
import re


class Script(BaseScript):
    name = "ZTE.ZXA10.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 240

    type = {
        "GUSQ": "gei_",
        "HUVQ": "gei_",
        "GMPA": "gei-",
        "GMRA": "gei-",
        "SFUQ": "xgei-",
        "SPUF": "xgei-",
        "XFTO": "xgei-",
        "GTGHK": "gpon-olt_",
        "GTGHG": "gpon-olt_",
        "GTGOG": "gpon-olt_",
        "GFCL": "gpon_olt-",
        "GFGL": "gpon_olt-",
        "GVGO": "gpon_olt-",
        "ETGHG": "epon-olt_",
        "VDWVD": "vdsl_",
        "SCXN": "gei_",
        "SCTM": "gei_",
        "SCXM": "gei_",
        "SCXL": "gei_",
        "SMXA": "gei_",
        "PTWVN": "",  # Telephone service
        "PRAM": "",
        "PRWGS": "",
    }
    rx_iface = re.compile(
        r"^\s*(?P<ifname>\S+) (?:admin status )?is (?P<admin_status>activate|deactivate|down|administratively down|up),\s*"
        r"line protocol is (?P<oper_status>down|up).*\n"
        r"(^\s*(?:Description|Byname) is (?P<descr>.+)\n)?",
        re.MULTILINE,
    )
    rx_vlan = re.compile(
        r"^(?P<mode>access=0|trunk\>0|hybrid\>=0|accessUn|trunk|access|hybrid)\s+(?P<pvid>\d+|--).+\n"
        r"(^\s*\n)?"
        r"^UntaggedVlan:\s*\n"
        r"(^\s*(?P<untagged>\d+)\s*\n)?"
        r"(^\s*\n)?"
        r"^TaggedVlan:\s*\n"
        r"(^\s*(?P<tagged>[\d,\-]+)\s*)?",
        re.MULTILINE,
    )
    rx_pvc = re.compile(
        r"^\s+Pvc (?P<pvc_no>\d+):\s*\n"
        r"^\s+Admin Status\s+:\s*(?P<admin_status>enable|disable)\s*\n"
        r"^\s+VPI/VCI\s+:\s*(?P<vpi>\d+)/(?P<vci>\d+)\s*\n",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"^(?P<ifname>\S+)\s+AdminStatus is (?P<admin_status>up|down),\s+"
        r"PhyStatus is (?:up|down),\s+line protocol is (?P<oper_status>up|down)\s*.*\n"
        r"(^\s+ip vrf forwarding .+\n)?"
        r"^\s+Internet address is (?P<ip>\S+)\s*\n"
        r"^\s+Broadcast address is .+\n"
        r"(^\s+Address determined by .+\n)?"
        r"(^\s+Load-sharing bandwidth .+\n)?"
        r"^\s+IP MTU (?:is )?(?P<mtu>\d+) bytes\s*\n",
        re.MULTILINE,
    )
    rx_ipv6 = re.compile(r"^\s+inet6 (?P<ipv6>\S+\d+)\s*\n", re.MULTILINE)
    rx_mac = re.compile(
        r"^\s+Description is (?P<descr>.+)\n^\s+MAC address is (?P<mac>\S+)\s*\n", re.MULTILINE
    )
    rx_mac2 = re.compile(r"^\s+Hardware address is (?P<mac>\S+)\s*\n", re.MULTILINE)
    rx_range = re.compile(r"^\s+<(?P<range>\d+(?:\-\d+)?)>", re.MULTILINE)

    def execute_cli(self):
        interfaces = []
        ports = self.profile.fill_ports(self)
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = self.profile.convert_interface_name(pc["interface"])
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
            interfaces += [
                {
                    "name": pc["interface"],
                    "type": "aggregated",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [
                        {
                            "name": pc["interface"],
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": ["BRIDGE"],
                        }
                    ],
                }
            ]
        for p in ports:
            if int(p["port"]) < 1 or p["realtype"] == "":
                continue
            prefix = self.type[p["realtype"]]
            if prefix in ["gpon-onu_", ""]:
                continue
            for i in range(int(p["port"])):
                port_num = "%s/%s/%s" % (p["shelf"], p["slot"], str(i + 1))
                ifname = "%s%s" % (prefix, port_num)
                try:
                    v = self.cli("show interface %s" % ifname)
                except self.CLISyntaxError:
                    # In some card we has both gei_ and xgei_ interfaces
                    if prefix == "gei_":
                        ifname = "xgei_%s" % port_num
                        v = self.cli("show interface %s" % ifname)
                    elif prefix == "gei-":
                        ifname = "xgei-%s" % port_num
                        v = self.cli("show interface %s" % ifname)
                    # In some card we have only `gpon_onu_` interfaces
                    elif prefix == "gpon-olt_" and p["realtype"] == "GTGOG":
                        continue
                match = self.rx_iface.search(v)
                admin_status = bool(match.group("admin_status") in ["up", "activate"])
                oper_status = bool(match.group("oper_status") == "up")
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "subinterfaces": [],
                }
                if match.group("descr"):
                    descr = match.group("descr").strip()
                    if descr not in ["none", "none.", "null"]:
                        iface["description"] = descr
                if prefix in ["gei_", "gpon-olt_", "epon-olt_", "gei-", "xgei-"]:
                    v = self.cli("show vlan port %s" % ifname)
                    match = self.rx_vlan.search(v)
                    sub = {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"],
                    }
                    if match.group("untagged"):
                        sub["untagged_vlan"] = match.group("untagged")
                    if match.group("tagged") and match.group("tagged") != "1":
                        sub["tagged_vlans"] = self.expand_rangelist(match.group("tagged"))
                    iface["subinterfaces"] += [sub]
                    if ifname in portchannel_members:
                        ai, is_lacp = portchannel_members[ifname]
                        iface["aggregated_interface"] = ai
                        iface["enabled_protocols"] = ["LACP"]
                if prefix in ["gpon_olt-", "epon_olt-"] and admin_status is True:
                    v = self.cli("show vlan port vport-%s.?" % port_num, command_submit=b"")
                    match1 = self.rx_range.search(v)
                    for dim1 in self.expand_rangelist(match1.group("range")):
                        v = self.cli(
                            "\x01\x0bshow vlan port vport-%s.%s:?" % (port_num, dim1),
                            command_submit=b"",
                        )
                        match2 = self.rx_range.search(v)
                        for dim2 in self.expand_rangelist(match2.group("range")):
                            v = self.cli(
                                "\x01\x0bshow vlan port vport-%s.%s:%s" % (port_num, dim1, dim2)
                            )
                            match3 = self.rx_vlan.search(v)
                            sub = {
                                "name": "vport-%s.%s:%s" % (port_num, dim1, dim2),
                                "admin_status": admin_status,
                                "oper_status": oper_status,
                                "enabled_afi": ["BRIDGE"],
                            }
                            if match3.group("untagged"):
                                sub["untagged_vlan"] = match3.group("untagged")
                            if match3.group("tagged"):
                                sub["tagged_vlans"] = self.expand_rangelist(match3.group("tagged"))
                            iface["subinterfaces"] += [sub]
                if prefix == "vdsl_":
                    for match in self.rx_pvc.finditer(v):
                        sub = {
                            "name": "%s.%s" % (ifname, match.group("pvc_no")),
                            "admin_status": match.group("admin_status") == "enable",
                            # "oper_status": oper_status  # need more examples
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "vpi": match.group("vpi"),
                            "vci": match.group("vci"),
                        }
                        iface["subinterfaces"] += [sub]
                interfaces += [iface]

        v = self.cli("show ip interface")
        for match in self.rx_ip.finditer(v):
            ifname = match.group("ifname")
            admin_status = bool(match.group("admin_status") == "up")
            oper_status = bool(match.group("oper_status") == "up")
            iface = {
                "name": ifname,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [match.group("ip")],
                        "mtu": match.group("mtu"),
                    }
                ],
            }
            try:
                c = self.cli("show interface %s" % ifname)
                match1 = self.rx_mac.search(c)
                iface["mac"] = match1.group("mac")
                iface["subinterfaces"][0]["mac"] = match1.group("mac")
            except self.CLISyntaxError:
                try:
                    c = self.cli("show ipv6 interface %s" % ifname)
                    match1 = self.rx_mac2.search(c)
                    iface["mac"] = match1.group("mac")
                    iface["subinterfaces"][0]["mac"] = match1.group("mac")
                    match1 = self.rx_ipv6.search(c)
                    if match1:
                        iface["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
                        iface["subinterfaces"][0]["ipv6_addresses"] = []
                        for match2 in self.rx_ipv6.finditer(c):
                            iface["subinterfaces"][0]["ipv6_addresses"] += [match2.group("ipv6")]
                except self.CLISyntaxError:
                    pass
            if ifname.startswith("vlan"):
                iface["type"] = "SVI"
                iface["subinterfaces"][0]["vlan_ids"] = [ifname[4:]]
            elif ifname == "mgmt_eth":
                iface["type"] = "management"
            else:
                raise self.NotSupportedError()
            interfaces += [iface]

        return [{"interfaces": interfaces}]
