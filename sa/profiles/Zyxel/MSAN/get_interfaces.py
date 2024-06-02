# ---------------------------------------------------------------------
# Zyxel.MSAN.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Zyxel.MSAN.get_interfaces"
    interface = IGetInterfaces

    rx_enet = re.compile(
        r"^\s*(?P<ifname>(enet|sub|up)\d+)\s+(?P<descr>.*?)\s+"
        r"(?P<admin_status>V|\-)\s+(?:sub|up)(?:tend|link)?\s+",
        re.MULTILINE,
    )
    rx_enet_o = re.compile(
        r"^\s*(switch )?port (?:enet|sub|up)\d+:\n\s*link status: (?P<oper_status>\S+|down)",
        re.MULTILINE,
    )
    rx_sub_pvc = re.compile(
        r"^\s*(?P<sub>\d+\-\d+)-(?P<vpi>\d+)/(?P<vci>\d+)\s+\S+\s+\S+\s+" r"(?P<pvid>\d+)\s+",
        re.MULTILINE,
    )
    rx_sub_pvc1 = re.compile(
        r"^\s*(?P<sub>\d+)\s+(?P<vpi>\d+)/(?P<vci>\d+)\s+\S+\s+(?P<pvid>\-|\d+)", re.MULTILINE
    )
    rx_sub_pvc2 = re.compile(
        r"^\s*(?P<sub>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+(?P<pvid>\S+)\s+", re.MULTILINE
    )
    rx_sub_o = re.compile(r"^\s*(?P<sub>\d+\s*\-\s*\d+)\s+(?P<admin_status>V|\-)", re.MULTILINE)
    rx_sub_o1 = re.compile(
        r"^\s*(?P<sub>\d+)\s+(?P<admin_status>V|\-)(\s+\S+\s+(?P<pvid>\d+))?", re.MULTILINE
    )
    rx_sub_o2 = re.compile(r"^\s*Port (?P<sub>\d+): (?P<admin_status>Up|Down)", re.MULTILINE)
    rx_sub_o3 = re.compile(
        r"^\s*(?:Port\=)?(?P<sub>\d+)\s.+(?P<admin_status>Enabled|Disabled)\s*/(?P<oper_status>Up|Down)\s*\n",
        re.MULTILINE,
    )
    rx_descr = re.compile(r"^\s*(?P<sub>\d+)\s+(?P<descr>\S+)\s+", re.MULTILINE)
    rx_ipif = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<mask>\d+\.\d+\.\d+\.\d+)\s*(?P<vid>\d+|\-)?\s*$",
        re.MULTILINE,
    )
    rx_ipif1 = re.compile(
        r"^\s*device\s+(?P<ifname>\S+)\s+\S+\s+\S+\s+mtu\s+(?P<mtu>\d+)\s+"
        r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mask>\d+\.\d+\.\d+\.\d+)\s*$",
        re.MULTILINE,
    )
    rx_ipif_mac = re.compile(r"^\s*(?P<ifname>\S+) mac\s+: (?P<mac>\S+)\s*\n", re.MULTILINE)
    rx_ipif_vlan = re.compile(r"^\s*host join vlan: (?P<vid>\d+)\s*\n", re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<ports>\S+)/(?P<mode>\S+)\s+\S+\s*" r"(?P<name>.*)$",
        re.MULTILINE,
    )
    rx_vlan1 = re.compile(
        r"^\s*\d+\s+(?:\-|msc)\s+(?P<ports>[\-FX]+)\s+(?P<mode>[TU]+)", re.MULTILINE
    )
    rx_vlan2 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s.+\n(^.+\n)?^\s+enabled\s+.+\n"
        r"^\s*(?P<ports>\S+) (?P<eports>\S+)\s*\n"
        r"^\s*(?P<mode>\S+) (?P<emode>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlan3 = re.compile(r"^\s*(?P<port>\S*\d+)\s+(?P<pvid>\d+)\s+.+\n", re.MULTILINE)
    rx_vlan4 = re.compile(r"^\s*(?P<vlan_id>\d+)\s+\-\s+(?P<tagged>v)\s+.+\n", re.MULTILINE)
    rx_vlan5 = re.compile(r"^\s*Port\s+0:\s+(?P<vlan_id>\d+)\s*\n", re.MULTILINE)
    rx_vlan6 = re.compile(r"^\s*Port\s+(?P<port>\d+):\s+(?P<vlan_id>\d+)\s*\n", re.MULTILINE)
    rx_mac = re.compile(r"^\s*mac address\s*: (?P<mac>\S+)\s*\n", re.MULTILINE | re.IGNORECASE)
    rx_ports = re.compile(
        r"^Port\s+\d+\s+\((?P<port>ethernet|adsl\d+|gshdsl\d+)\): " r"(?:Enabled|Disabled)\s*\n",
        re.MULTILINE,
    )
    rx_stp = re.compile(r"^\s*(?P<port>\S+)\s+V\s+\d+\s+", re.MULTILINE)

    def get_stp(self):
        try:
            v = self.cli("switch port mstp show 0")
        except self.CLISyntaxError:
            return []
        r = []
        for match in self.rx_stp.finditer(v):
            r += [match.group("port")]
        return r

    def execute_cli(self):
        slots = self.profile.get_slots_n(self)
        interfaces = []
        iface_mac = []
        vlans = []
        if_pvid = {}
        stps = self.get_stp()
        if slots > 1:
            try:
                v = self.cli("vlan show")
                for match in self.rx_vlan.finditer(v):
                    vlans += [
                        {
                            "vid": int(match.group("vlan_id")),
                            "ports": match.group("ports"),
                            "mode": match.group("mode"),
                        }
                    ]
            except self.CLISyntaxError:
                for vlan in self.scripts.get_vlans():
                    v = self.cli("lcman svlan show %s" % vlan["vlan_id"])
                    match = self.rx_vlan1.search(v)
                    vlans += [
                        {
                            "vid": int(vlan["vlan_id"]),
                            "ports": match.group("ports"),
                            "mode": match.group("mode"),
                        }
                    ]
            port_num = 0
            c = self.cli("switch port show")
            if "usage" in c:
                c = self.cli("switch port show all")
            has_enet = True
            for match in self.rx_enet.finditer(c):
                untagged = 0
                tagged = []
                admin_status = match.group("admin_status") == "V"
                ifname = self.profile.convert_interface_name(match.group("ifname"))
                if has_enet:
                    try:
                        e = self.cli("show enet %s" % ifname)
                        match1 = self.rx_enet_o.search(e)
                        if match1:
                            oper_status = match1.group("oper_status") != "down"
                        else:
                            raise self.NotSupportedError()
                    except self.CLISyntaxError:
                        has_enet = False
                        oper_status = admin_status
                else:
                    oper_status = admin_status
                for v in vlans:
                    if v["ports"][port_num] == "F" and v["mode"][port_num] == "U":
                        untagged = v["vid"]
                    if v["ports"][port_num] == "F" and v["mode"][port_num] == "T":
                        tagged += [v["vid"]]
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "hints": ["noc::topology::direction::nni", "technology::ethernet::1000base"],
                    "enabled_protocols": [],
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "enabled_afi": ["BRIDGE"],
                        }
                    ],
                }
                if untagged:
                    iface["subinterfaces"][0]["untagged_vlan"] = untagged
                if tagged:
                    iface["subinterfaces"][0]["tagged_vlans"] = tagged
                if ifname in stps:
                    iface["enabled_protocols"] += ["STP"]
                interfaces += [iface]
                port_num += 1
            port_show = True
            for i in range(1, slots + 1):
                if port_show:
                    try:
                        v = self.cli("port show %s" % i)
                        rx_sub = self.rx_sub_o
                    except self.CLISyntaxError:
                        port_show = False
                        v = self.cli("lcman port show %s" % i)
                        rx_sub = self.rx_sub_o1
                    if "must not be empty" in v:
                        continue
                    descrs = []
                else:
                    v = self.cli("lcman port show %s" % i)
                    if "must not be empty" in v:
                        continue
                    d = self.cli("lcman port description show %s" % i)
                    descrs = self.rx_descr.findall(d)
                for match in rx_sub.finditer(v):
                    admin_status = match.group("admin_status") == "V"
                    sub = match.group("sub")
                    ifname = sub.replace(" ", "")
                    if not port_show:
                        ifname = "%s/%s" % (i, ifname)
                    if "pvid" in match.groupdict() and match.group("pvid"):
                        if_pvid[ifname] = match.group("pvid")
                    iface = {
                        "name": ifname,
                        "admin_status": admin_status,
                        "type": "physical",
                        "subinterfaces": [],
                    }
                    for d in descrs:
                        if d[0] == sub and d[1] != "-":
                            iface["description"] = d[1]
                            break
                    interfaces += [iface]
                if port_show:
                    v = self.cli("port show %s pvc" % i)
                    rx_pvc = self.rx_sub_pvc
                else:
                    v = self.cli("lcman port pvc show %s" % i)
                    rx_pvc = self.rx_sub_pvc1
                for match in rx_pvc.finditer(v):
                    if port_show:
                        ifname = match.group("sub")
                    else:
                        ifname = "%s/%s" % (i, match.group("sub"))
                    for iface in interfaces:
                        if iface["name"] == ifname:
                            if match.group("pvid") == "-":
                                pvid = if_pvid.get(ifname, 1)
                            else:
                                pvid = int(match.group("pvid"))
                            iface["subinterfaces"] += [
                                {
                                    "name": "%s.%s" % (ifname, match.group("pvid")),
                                    "admin_status": iface["admin_status"],
                                    "enabled_afi": ["BRIDGE", "ATM"],
                                    "vlan_ids": pvid,
                                    "vpi": int(match.group("vpi")),
                                    "vci": int(match.group("vci")),
                                }
                            ]
                            break
                v = self.cli("lcman show %s" % i)
                for match in self.rx_ipif_mac.finditer(v):
                    iface_mac += [match.groupdict()]
        else:
            # We are not use `matchers`, because it not have `Boot PROM` field
            ver = self.scripts.get_version()
            b_prom = self.capabilities.get("Chassis | Boot PROM")
            if ver["platform"] == "IES-1000" and b_prom and "AAM1212" in b_prom:
                new_syntax = True
            else:
                new_syntax = False

            if ver["platform"] in ["IES-1248", "IES-612"] or new_syntax:
                v = self.cli("switch vlan show *")
                for match in self.rx_vlan2.finditer(v):
                    vlans += [
                        {
                            "vid": int(match.group("vlan_id")),
                            "ports": "%s%s" % (match.group("ports"), match.group("eports")),
                            "mode": "%s%s" % (match.group("mode"), match.group("emode")),
                        }
                    ]
                port_num = 0
                v = self.cli("switch vlan portshow")
                for match in self.rx_vlan3.finditer(v):
                    untagged = 0
                    tagged = []
                    ifname = self.profile.convert_interface_name(match.group("port"))
                    for v in vlans:
                        if v["ports"][port_num] == "F" and v["mode"][port_num] == "U":
                            untagged = v["vid"]
                        if v["ports"][port_num] == "F" and v["mode"][port_num] == "T":
                            tagged += [v["vid"]]
                    iface = {"name": ifname, "type": "physical", "subinterfaces": []}
                    if ifname.startswith("Enet"):
                        iface["hints"] = [
                            "noc::topology::direction::nni",
                            "technology::ethernet::1000base",
                        ]
                        iface["subinterfaces"] += [{"name": ifname, "enabled_afi": ["BRIDGE"]}]
                        if untagged:
                            iface["subinterfaces"][0]["untagged_vlan"] = untagged
                        if tagged:
                            iface["subinterfaces"][0]["tagged_vlans"] = tagged
                    interfaces += [iface]
                    port_num += 1
                v = self.cli("adsl pvc show")
                for match in self.rx_sub_pvc2.finditer(v):
                    ifname = match.group("sub")
                    for i in interfaces:
                        if ifname == i["name"]:
                            sub = {
                                "name": ifname,
                                "enabled_afi": ["BRIDGE", "ATM"],
                                "vpi": int(match.group("vpi")),
                                "vci": int(match.group("vci")),
                            }
                            if match.group("pvid") != "*":
                                sub["vlan_ids"] = int(match.group("pvid"))
                            i["subinterfaces"] += [sub]
                match = self.rx_mac.search(self.cli("sys info show"))
                iface_mac += [{"ifname": "Ethernet", "mac": match.group("mac")}]
            elif ver["platform"] in ["IES-1000"]:
                try:
                    adsl = self.cli("adsl show ports")
                except self.CLISyntaxError:
                    adsl = self.cli("gshdsl list ports")
                vlans_pvid = self.cli("vlan1q vlan status")
                v = self.cli("bridge macfilter")
                for match in self.rx_ports.finditer(v):
                    ifname = match.group("port")
                    iface = {"name": ifname, "type": "physical", "subinterfaces": []}
                    if ifname.startswith("ethernet"):
                        sub = {
                            "name": ifname,
                            "admin_status": True,
                            "enabled_afi": ["BRIDGE"],
                            "tagged_vlans": [],
                        }
                        for match in self.rx_vlan4.finditer(vlans_pvid):
                            vid = int(match.group("vlan_id"))
                            if vid == 1:
                                continue
                            sub["tagged_vlans"] += [vid]
                        iface["subinterfaces"] += [sub]
                        iface["hints"] = [
                            "noc::topology::direction::nni",
                            "technology::ethernet::1000base",
                        ]
                        interfaces += [iface]
                    if ifname.startswith("adsl"):
                        for match in self.rx_sub_o2.finditer(adsl):
                            if match.group("sub") == ifname[4:]:
                                iface["admin_status"] = match.group("admin_status") == "Up"
                                break
                        v = self.cli("adsl show pvc %s" % ifname[4:])
                        for match in self.rx_sub_pvc2.finditer(v):
                            iface["subinterfaces"] += [
                                {
                                    "name": match.group("sub"),
                                    "admin_status": iface["admin_status"],
                                    "enabled_afi": ["BRIDGE", "ATM"],
                                    "vlan_ids": (
                                        int(match.group("pvid"))
                                        if match.group("pvid") != "*"
                                        else None
                                    ),
                                    "vpi": int(match.group("vpi")),
                                    "vci": int(match.group("vci")),
                                }
                            ]
                        iface["hints"] = ["technology::dsl::adsl"]
                        interfaces += [iface]
                    if ifname.startswith("gshdsl"):
                        for match in self.rx_sub_o3.finditer(adsl):
                            if match.group("sub") == ifname[6:]:
                                iface["admin_status"] = match.group("admin_status") == "Enabled"
                                iface["oper_status"] = match.group("oper_status") == "Up"
                                break
                        vid = 1
                        for match in self.rx_vlan6.finditer(vlans_pvid):
                            if match.group("port") == ifname[6:]:
                                vid = int(match.group("vlan_id"))
                                break
                        v = self.cli("gshdsl show pvc %s" % ifname[6:])
                        match = self.rx_sub_pvc2.search(v)
                        sub = {
                            "name": match.group("sub"),
                            "admin_status": iface["admin_status"],
                            "oper_status": iface["oper_status"],
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "vpi": int(match.group("vpi")),
                            "vci": int(match.group("vci")),
                        }
                        if match.group("pvid") != "*":
                            sub["vlan_ids"] = int(match.group("pvid"))
                        elif vid != 1:
                            sub["vlan_ids"] = int(vid)
                        iface["hints"] = ["technology::dsl::shdsl"]
                        iface["subinterfaces"] = [sub]
                        interfaces += [iface]
                c = self.cli("ip device list")
                for match in self.rx_ipif1.finditer(c):
                    ifname = match.group("ifname")
                    addr = match.group("ip")
                    mask = match.group("mask")
                    ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
                    iface = {
                        "name": ifname,
                        "type": "SVI",
                        "admin_status": True,  # always True, since inactive
                        "oper_status": True,  # SVIs aren't shown at all
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "admin_status": True,
                                "oper_status": True,
                                "mtu": int(match.group("mtu")),
                                "enabled_afi": ["IPv4"],
                                "ipv4_addresses": [ip_address],
                            }
                        ],
                    }
                    v = self.cli("vlan1q vlan status")
                    match1 = self.rx_vlan5.search(v)
                    vid = int(match1.group("vlan_id"))
                    iface["subinterfaces"][0]["vlan_ids"] = [vid]
                    ch_id = self.scripts.get_chassis_id()
                    mac = ch_id[0]["first_chassis_mac"]
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
                    interfaces += [iface]
                return [{"interfaces": interfaces}]

        try:
            c = self.cli("ip show")
        except self.CLISyntaxError:
            c = self.cli("ip device")
        for match in self.rx_ipif.finditer(c):
            ifname = match.group("ifname")
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": True,  # always True, since inactive
                "oper_status": True,  # SVIs aren't shown at all
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip_address],
                    }
                ],
            }
            if (match.group("vid") is not None) and (match.group("vid") != "-"):
                iface["subinterfaces"][0]["vlan_ids"] = [int(match.group("vid"))]
            else:
                if match.group("vid") is None:
                    v = self.cli("switch vlan cpu show")
                    match1 = self.rx_ipif_vlan.search(v)
                    iface["subinterfaces"][0]["vlan_ids"] = [int(match1.group("vid"))]
            for m in iface_mac:
                if ifname == m["ifname"]:
                    iface["mac"] = m["mac"]
                    iface["subinterfaces"][0]["mac"] = m["mac"]
            interfaces += [iface]
        for match in self.rx_ipif1.finditer(c):
            ifname = match.group("ifname")
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": True,  # always True, since inactive
                "oper_status": True,  # SVIs aren't shown at all
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip_address],
                    }
                ],
            }
            for m in iface_mac:
                if ifname == m["ifname"]:
                    iface["mac"] = m["mac"]
                    iface["subinterfaces"][0]["mac"] = m["mac"]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
