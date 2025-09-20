# ---------------------------------------------------------------------
# DLink.DxS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Optional, Iterable, Callable, Tuple, Union

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.validators import is_int
from noc.sa.profiles.DLink.DxS.profile import DxS_L2, DGS3120, DGS3420, DGS3620
from noc.core.mib import mib
from noc.core.snmp.render import render_bin


class Script(BaseScript):
    name = "DLink.DxS.get_interfaces"
    interface = IGetInterfaces

    rx_port_no = re.compile(r"^(?P<unit>\d+)[:/](?P<port>\d+)$")
    rx_ipif1 = re.compile(
        r"(?:Interface Name|IP Interface)\s+:\s+(?P<ifname>\S+)\s*\n"
        r"IP Address\s+:\s+(?P<ip_address>\S+)\s+\(\S+\)\s*\n"
        r"(Secondary\s+: (?P<secondary>\S+)\s*\n)?"
        r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n"
        r"VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
        r"(?:Interface )?Admin.? State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
        r"(Proxy ARP\s+: \S+\s*\n)?"
        r"(DHCPv6 Client State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
        r"Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n"
        r"Member Ports\s+:\s*\S*\s*\n"
        r"(IPv6 Link-Local Address\s+:\s+\S+\s*\n)?"
        r"(IPv6 Global Unicast Address\s+:\s+(?P<ipv6_address>\S+)\s*\n)?"
        r"(DHCP Option12 State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
        r"(DHCP Option12 Host Name\s+:\s*\S*\s*\n)?"
        r"(Description\s+:\s*(?P<desc>\S*?)\s*\n)?",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    rx_ipif2 = re.compile(
        r"IP Interface\s+:\s+(?P<ifname>\S+)\s*\n"
        r"VLAN Name\s+:\s+(?P<vlan_name>\S*)\s*\n"
        r"Interface Admin.? State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
        r"(DHCPv6 Client State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
        r"(Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n)?"
        r"(IP(v4)? Address\s+:\s+(?P<ipv4_address>\S+)\s+\(\S+\)\s*\n)?"
        r"(IPv4 Address\s+:\s+(?P<ipv4_addr_pri>\S+)\s+\(\S+\)\s+Primary\s*\n)?"
        r"(Proxy ARP\s+:\s+(?:Enabled|Disabled)\s+\(Local : \S+\s*\)\s*\n)?"
        r"(IPv4 State\s+:\s+(?P<is_ipv4>Enabled|Disabled)\s*\n)?"
        r"(IPv6 State\s+:\s+(?P<is_ipv6>Enabled|Disabled)\s*\n)?"
        r"(IP Directed Broadcast\s+:\s+(?:Enabled|Disabled)\s*\n)?"
        r"(IPv6 Link-Local Address\s+:\s+\S+\s*\n)?"
        r"(IPv6 Global Unicast Address\s+:\s+(?P<ipv6_address>\S+) \(\S+\)\s*\n)?"
        r"(IP MTU\s+:\s+(?P<mtu>\d+)\s+\n)?",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    # Work only on DES-1210-XX/ME/BX
    rx_ipif3 = re.compile(
        r"IP Interface\s+:\s+(?P<ifname>.+?)\s*\n"
        r"VLAN Name\s+:\s+(?P<vlan_name>\S*)\s*\n"
        r"Interface Admin.? State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
        r"(IPv4 Address\s+:\s+(?P<ipv4_address>\S+)\s+\(\S+\)\s*\n)?"
        r"(IPv6 Link-Local Address\s+:\s+\S+\s*\n)?"
        r"(IPv6 Global Unicast Address\s+:\s+(?P<ipv6_address>\S+) \(\S+\)\s*\n)?"
        r"(DHCPv6 Client State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
        r"(IPv4 State\s+:\s+(?P<is_ipv4>Enabled|Disabled)\s*\n)?"
        r"(IPv6 State\s+:\s+(?P<is_ipv6>Enabled|Disabled)\s*\n)?",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    # Work only on DGS-1210-XX/ME/BX
    rx_ipif4 = re.compile(
        r"Interface Name\s+:\s+(?P<ifname>\S+)\s*\n"
        r"Interface VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
        r"IP Address\s+:\s+(?P<ip_address>\S+)\s*\n"
        r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n"
        r"Default Gateway\s+:.+\n"
        r"Interface Admin State\s+:\s+(?P<admin_state>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE,
    )
    rx_ipmgmt = re.compile(
        r"IP Interface\s+:\s+(?P<ifname>mgmt_ipif)\s*\n"
        r"Status\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
        r"IP Address\s+:\s+(?P<ip_address>\S+)\s*\n"
        r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n"
        r"(Gateway\s+:\s+\S+\s*\n)?"
        r"Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    rx_ipswitch = re.compile(
        r"MAC Address\s+:\s*(?P<mac_address>\S+)\s*\n"
        r"IP Address\s+:\s*(?P<ip_address>\S+)\s*\n"
        r"VLAN Name\s+:\s*(?P<vlan_name>\S+)\s*\n"
        r"Subnet Mask\s+:\s*(?P<ip_subnet>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    rx_ipif_des_a1 = re.compile(
        r"IP Address\s+:\s*(?P<ip_address>\S+)\s*\nSubnet Mask\s+:\s*(?P<ip_subnet>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_mgmt_vlan = re.compile(
        r"^management vlan id\s+:\s+(?P<vlan_id>\d+)",
        re.MULTILINE,
    )
    rx_mac = re.compile(r"^MAC Address\s+:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_link_up = re.compile(r"Link\s*UP", re.IGNORECASE)
    rx_rip_gs = re.compile(r"RIP Global State : Enabled")
    rx_ospf_gs = re.compile(r"OSPF Router ID : \S+( \(.+\))?\s*\nState\s+: Enabled")
    rx_ospfv3_gs = re.compile(r"OSPFv3 Router ID : \S+( \(.+\))?\s*\nState\s+: Enabled")
    rx_ctp_gs = re.compile(r"(LBD )?Status\s+: Enabled")
    rx_pim_gs = re.compile(r"PIM Global State\s+: Enabled")
    rx_gvrp_gs = re.compile(r"Global GVRP\s+: Enabled")
    rx_dvmrp_gs = re.compile(r"DVMRP Global State\s+: Enabled")
    rx_rip = re.compile(
        r"(?P<ipif>\S+)\s+\S+\s+(?:Disabled|Enabled)\s+"
        r"(?:Disabled|Enabled)\s+(?:Disabled|Enabled)\s+Enabled\s*"
    )
    rx_ospf = re.compile(
        r"(?P<ipif>\S+)\s+\S+\s+\S+\s+Enabled\s+" r"Link (?:Up|DOWN)\s+\d+", re.IGNORECASE
    )
    rx_ospfv3 = re.compile(
        r"(?P<ipif>\S+)\s+\S+\s+Enabled\s+" r"Link (?:Up|DOWN)\s+\d+", re.IGNORECASE
    )
    rx_lldp = re.compile(
        r"Port ID\s+:\s+(?P<port>\d+(?:[:/]\d+)?)\s*\n"
        r"\-+\s*\nAdmin Status\s+: (?:TX_and_RX|RX_Only|TX_Only)"
    )
    rx_lldp1 = re.compile(
        r"Port ID\s+:\s+(?P<port>\d+(?:[:/]\d+)?)\s*\n"
        r"\-+\s*\nPort ID Subtype\s+: MAC Address\s*\n"
        r"Port ID\s+: (?P<mac>\S+)"
    )
    rx_pd = re.compile(
        r"Port\s+:\s+(?P<port>\d+(?:[:/]\d+)?)\s*\n"
        r"\-+\s*\nPort Status\s+: Link (?:Up|Down)\s*\n"
        r"Description\s+:\s*(?P<desc>.*?)\s*\n"
        r"HardWare Type\s+:\s*.+\s*\n"
        r"MAC Address\s+:\s*(?P<mac>\S+)\s*\n"
    )
    rx_ctp = re.compile(
        r"^(?P<port>\d+(?:[:/]\d+)?)\s+(?P<status>Enabled|Disabled)\s+\S+", re.MULTILINE
    )
    rx_pim = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\S+\s+\d+\s+\d+\s+\S+\s+Enabled\s+")
    rx_igmp = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+Enabled\s+")
    rx_dvmrp = re.compile(r"(?P<ipif>\S+)\s+\S+\s+\d+\s+\d+\s+\d+\s+Enabled\s+")
    rx_gvrp = re.compile(r"^ (?P<port>\d+(?:[:/]\d+)?)\s+\d+\s+Enabled")
    rx_stp = re.compile(
        r"Port Index\s+: (?P<port>\d+(?:[:/]\d+)?)\s+.+?"
        r"Port STP (: )?(?P<state>[Ee]nabled|[Dd]isabled)"
    )
    rx_stp1 = re.compile(
        r"Port Index\s+: (?P<port>\d+(?:[:/]\d+)?)\s*\n"
        r"Connection\s+: Link (?:Up|Down)\s*\n"
        r"State : (?:Yes|Enabled)"
    )
    rx_stp2 = re.compile(r"^(?P<port>\d+(?:[:/]\d+)?)\s+\S+\/\S+\s+Yes", re.MULTILINE)
    rx_oam = re.compile(
        r"^Port (?P<port>\d+(?:[:/]\d+)?)\s*\n\-+\s*\nOAM\s+:\s+Enabled\s*\n", re.MULTILINE
    )
    rx_trunk = re.compile(
        r"Group ID\s+:\s+(?P<trunk>\d+).+?Type\s+:\s+(?P<type>\S+).+?"
        r"Member Port\s+:\s+(?P<members>\S+).+?Status\s+:\s+(?P<status>\S+)",
        re.MULTILINE | re.DOTALL,
    )

    INTERFACE_TYPES = {
        1: "other",
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        117: "physical",  # gigabitEthernet
        142: "SVI",  # ipForwadr
        161: "aggregated",  # ieee8023adLag
    }

    def get_max_repetitions(self):
        if self.is_dgs:
            return 20
        return self.MAX_REPETITIONS

    def iter_iftable(
        self, key: str, oid: str, ifindexes: Optional[Iterable[int]] = None, clean: Callable = None
    ) -> Iterable[Tuple[str, Union[str, int]]]:
        if key == "mac" and self.is_bad_ifmib_snmp:
            oid = "LLDP-MIB::lldpLocPortId"
        return super().iter_iftable(key=key, oid=oid, ifindexes=ifindexes, clean=clean)

    def clean_iftype(self, ifname: str, ifindex: Optional[int] = None) -> str:
        if not getattr(self, "_iftype_map", None):
            self._iftype_map = {
                int(oid.split(".")[-1]): iftype
                for oid, iftype in self.snmp.getnext(mib["IF-MIB::ifType"])
            }
        iftype = self.INTERFACE_TYPES.get(self._iftype_map[ifindex], "other")
        if iftype is None:
            return self.profile.get_interface_type(ifname)
        return iftype

    def get_iftable(self, oid, transform=True):
        if "::" in oid:
            oid = mib[oid]
        for oid, v in self.snmp.getnext(
            oid, max_repetitions=40, display_hints={"1.0.8802.1.1.2.1.3.7.1.3": render_bin}
        ):
            yield int(oid.rsplit(".", 1)[-1]) if transform else oid, v

    def apply_table(self, r, mib, name, f=None):
        if not f:

            def f(x):
                return x

        for ifindex, v in self.get_iftable(mib):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def parse_ctp(self, s):
        match = self.rx_ctp.search(s)
        if match:
            key = match.group("port")
            obj = {"port": key, "status": match.group("port")}
            return key, obj, s[match.end() :]
        else:
            return None

    def parse_stp(self, s):
        match = self.rx_stp.search(s)
        if not match:
            match = self.rx_stp1.search(s)
            if not match:
                match = self.rx_stp2.search(s)
        if match:
            key = match.group("port")
            obj = {"port": key}
            return key, obj, s[match.end() :]
        else:
            return None

    def execute_cli(self):
        if self.is_dgs_1100:
            print("This platform has ugly CLI support, passing")
            return []
        ipif_found = False
        if self.match_version(DxS_L2):
            L2_Switch = True
        else:
            L2_Switch = False

            rip = []
            try:
                c = self.cli("show rip")
                if self.rx_rip_gs.search(c) is not None:
                    rip = self.rx_rip.findall(c)
            except self.CLISyntaxError:
                pass

            ospf = []
            try:
                c = self.cli("show ospf")
                if self.rx_ospf_gs.search(c) is not None:
                    ospf = self.rx_ospf.findall(c)
            except self.CLISyntaxError:
                pass

            ospfv3 = []
            try:
                c = self.cli("show ospfv3")
                if self.rx_ospfv3_gs.search(c) is not None:
                    ospfv3 = self.rx_ospfv3.findall(c)
            except self.CLISyntaxError:
                pass

            pim = []
            try:
                c = self.cli("show pim")
                if self.rx_pim_gs.search(c) is not None:
                    pim = self.rx_pim.findall(c)
            except self.CLISyntaxError:
                pass

            dvmrp = []
            try:
                c = self.cli("show dvmrp")
                if self.rx_dvmrp_gs.search(c) is not None:
                    dvmrp = self.rx_dvmrp.findall(c)
            except self.CLISyntaxError:
                pass

            try:
                c = self.cli("show igmp")
                igmp = self.rx_igmp.findall(c)
            except self.CLISyntaxError:
                igmp = []

        lldp = []
        if self.has_capability("Network | LLDP"):
            try:
                c = self.cli("show lldp ports")
                lldp = self.rx_lldp.findall(c)
            except self.CLISyntaxError:
                pass

        macs = {}
        try:
            c = self.cli("show lldp local_ports mode brief")
            for match in self.rx_lldp1.finditer(c):
                macs[match.group("port")] = match.group("mac")
        except self.CLISyntaxError:
            pass

        if len(macs) == 0:
            if self.match_version(DGS3620, version__gte="2.60.16") or self.match_version(
                DGS3120, version__gte="4.00.00"
            ):
                try:
                    c = self.cli("show ports details")
                    for match in self.rx_pd.finditer(c):
                        macs[match.group("port")] = match.group("mac")
                except self.CLISyntaxError:
                    pass

        ctp = []
        try:
            c = self.cli("show loopdetect")
        except self.CLISyntaxError:
            c = ""
        ctp_enable = self.rx_ctp_gs.search(c) is not None
        if ctp_enable:
            c = []
            try:
                c = self.cli(
                    "show loopdetect ports all",
                    obj_parser=self.parse_ctp,
                    cmd_next="n",
                    cmd_stop="q",
                )
            except self.CLISyntaxError:
                c = []
            if not c:
                c = self.cli(
                    "show loopdetect ports", obj_parser=self.parse_ctp, cmd_next="n", cmd_stop="q"
                )
            for i in c:
                if i["status"] == "Enabled":
                    ctp += [i["port"]]

        gvrp = []
        try:
            c = self.cli("show gvrp")
            if self.rx_gvrp_gs.search(c) is not None:
                try:
                    c1 = self.cli("show port_vlan")
                except self.CLISyntaxError:
                    c1 = c
                    gvrp = self.rx_gvrp.findall(c1)
        except self.CLISyntaxError:
            pass

        stp = []
        if self.has_capability("Network | STP"):
            c = self.cli(
                "show stp ports", obj_parser=self.parse_stp, cmd_next="n", cmd_stop="q", cached=True
            )
            for i in c:
                stp += [i["port"]]

        oam = []
        if self.has_capability("Network | OAM"):
            try:
                c = self.cli("show ethernet_oam ports configuration")
                oam = self.rx_oam.findall(c)
            except self.CLISyntaxError:
                pass

        ports = self.profile.get_ports(self)
        vlans = self.profile.get_vlans(self)
        fdb = self.scripts.get_mac_address_table()

        interfaces = []
        for p in ports:
            ifname = p["port"]
            i = {
                "name": ifname,
                "type": "physical",
                "admin_status": p["admin_state"],
                "oper_status": p["status"],
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": p["admin_state"],
                        "oper_status": p["status"],
                        # "ifindex": 1,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            desc = p["desc"]
            if desc != "" and desc != "null":
                i["description"] = desc
                i["subinterfaces"][0]["description"] = desc
            mac = macs.get(ifname)
            if mac:
                i["mac"] = mac
                i["subinterfaces"][0]["mac"] = mac
            if is_int(ifname):
                i["snmp_ifindex"] = int(ifname)
            else:
                match = self.rx_port_no.search(ifname)
                if match:
                    unit_no = int(match.group("unit"))
                    port_no = int(match.group("port"))
                    i["snmp_ifindex"] = int(port_no + (unit_no - 1) * 64)
            tagged_vlans = []
            for v in vlans:
                if p["port"] in v["tagged_ports"]:
                    tagged_vlans += [v["vlan_id"]]
                if p["port"] in v["untagged_ports"]:
                    i["subinterfaces"][0]["untagged_vlan"] = v["vlan_id"]
            if len(tagged_vlans) != 0:
                i["subinterfaces"][0]["tagged_vlans"] = tagged_vlans
            if ifname in lldp:
                i["enabled_protocols"] += ["LLDP"]
            if ifname in ctp:
                i["enabled_protocols"] += ["CTP"]
            if ifname in gvrp:
                i["enabled_protocols"] += ["GVRP"]
            if ifname in stp:
                i["enabled_protocols"] += ["STP"]
            if ifname in oam:
                i["enabled_protocols"] += ["OAM"]
            interfaces += [i]

        try:
            c = self.cli("show link_aggregation")
        except self.CLISyntaxError:
            c = ""
        for match in self.rx_trunk.finditer(c):
            ifname = "T%s" % match.group("trunk")
            ifstatus = match.group("status").lower() == "enabled"
            i = {
                "name": ifname,
                "type": "aggregated",
                "admin_status": ifstatus,
                "oper_status": ifstatus,
                "enabled_protocols": [],
                # 896=64*14 - obtained from DGS-3420-28SC
                "snmp_ifindex": 896 + int(match.group("trunk")),
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": ifstatus,
                        "oper_status": ifstatus,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            lacp_proto = match.group("type").lower() == "lacp"
            members = self.expand_interface_range(match.group("members"))
            for iface in interfaces:
                if iface["name"] in members:
                    iface["aggregated_interface"] = ifname
                    if lacp_proto:
                        iface["enabled_protocols"] += ["LACP"]
            interfaces += [i]

        ipif = self.cli("show ipif")
        for match in self.rx_ipif1.finditer(ipif):
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            oper_status = self.rx_link_up.match(o_status) is not None
            i = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            desc = match.group("desc")
            if desc is not None and desc != "":
                desc = desc.strip()
                i["description"] = desc
                i["subinterfaces"][0]["description"] = desc
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            ipv6_address = match.group("ipv6_address")
            if ipv6_address is not None:
                i["subinterfaces"][0]["ipv6_addresses"] = [ipv6_address]
                i["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
            vlan_name = match.group("vlan_name")
            for v in vlans:
                if vlan_name == v["vlan_name"]:
                    vlan_id = v["vlan_id"]
                    i["subinterfaces"][0]["vlan_ids"] = [vlan_id]
                    for f in fdb:
                        if "CPU" in f["interfaces"] and vlan_id == f["vlan_id"]:
                            i["mac"] = f["mac"]
                            i["subinterfaces"][0]["mac"] = f["mac"]
                            break
                    break
            if match.group("secondary") and match.group("secondary") == "TRUE":
                interfaces[-1]["subinterfaces"][0]["ipv4_addresses"] += i["subinterfaces"][0][
                    "ipv4_addresses"
                ]
            else:
                interfaces += [i]
            ipif_found = True

        for match in self.rx_ipif2.finditer(ipif):
            enabled_afi = []
            enabled_protocols = []
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            if o_status is not None:
                oper_status = self.rx_link_up.match(o_status) is not None
            else:
                oper_status = admin_status
            ifname = match.group("ifname")
            i = {
                "name": ifname,
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": [],
                    }
                ],
            }
            mtu = match.group("mtu")
            if mtu is not None:
                i["subinterfaces"][0]["mtu"] = int(mtu)
            # TODO: Parse secondary IPv4 address and IPv6 address
            ipv4_addresses = []
            ipv4_address = match.group("ipv4_address")
            if ipv4_address is not None:
                ipv4_addresses += [ipv4_address]
                if "IPv4" not in enabled_afi:
                    enabled_afi += ["IPv4"]
            ipv4_addr_pri = match.group("ipv4_addr_pri")
            if ipv4_addr_pri is not None:
                ipv4_addresses += [ipv4_addr_pri]
                if "IPv4" not in enabled_afi:
                    enabled_afi += ["IPv4"]
            if ipv4_address is not None or ipv4_addr_pri is not None:
                i["subinterfaces"][0].update({"ipv4_addresses": ipv4_addresses})
            ipv6_address = match.group("ipv6_address")
            if ipv6_address is not None:
                i["subinterfaces"][0]["ipv6_addresses"] = [ipv6_address]
                enabled_afi += ["IPv6"]
            i["subinterfaces"][0].update({"enabled_afi": enabled_afi})
            vlan_name = match.group("vlan_name")
            # Found illegal stuff in DES-1210-28/ME/B2
            # In this rotten device System interface always in vlan 1
            if not vlan_name:
                vlan_name = "default"
            for v in vlans:
                if vlan_name == v["vlan_name"]:
                    vlan_id = v["vlan_id"]
                    i["subinterfaces"][0]["vlan_ids"] = [vlan_id]
                    for f in fdb:
                        if "CPU" in f["interfaces"] and vlan_id == f["vlan_id"]:
                            i["mac"] = f["mac"]
                            i["subinterfaces"][0]["mac"] = f["mac"]
                            break
                    break
            if not L2_Switch:
                if ifname in rip:
                    enabled_protocols += ["RIP"]
                if ifname in ospf:
                    enabled_protocols += ["OSPF"]
                if ifname in ospfv3:
                    enabled_protocols += ["OSPFv3"]
                if ifname in pim:
                    enabled_protocols += ["PIM"]
                if ifname in dvmrp:
                    enabled_protocols += ["DVMRP"]
                if ifname in igmp:
                    enabled_protocols += ["IGMP"]
                i["subinterfaces"][0]["enabled_protocols"] = enabled_protocols
            interfaces += [i]
            ipif_found = True

        for match in self.rx_ipif4.finditer(ipif):
            admin_status = match.group("admin_state") == "Enable"
            oper_status = admin_status
            ifname = match.group("ifname")
            i = {
                "name": ifname,
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            vlan_name = match.group("vlan_name")
            if not vlan_name:
                vlan_name = "default"
            for v in vlans:
                if vlan_name == v["vlan_name"]:
                    vlan_id = v["vlan_id"]
                    i["subinterfaces"][0]["vlan_ids"] = [vlan_id]
                    for f in fdb:
                        if "CPU" in f["interfaces"] and vlan_id == f["vlan_id"]:
                            i["mac"] = f["mac"]
                            i["subinterfaces"][0]["mac"] = f["mac"]
                            break
                    break
            interfaces += [i]
            ipif_found = True

        if self.match_version(DGS3420) or self.match_version(DGS3620):
            match = self.rx_ipmgmt.search(ipif)
            if match:
                admin_status = match.group("admin_state") == "Enabled"
                o_status = match.group("oper_status")
                oper_status = self.rx_link_up.match(o_status) is not None
                i = {
                    "name": match.group("ifname"),
                    "type": "management",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "subinterfaces": [
                        {
                            "name": match.group("ifname"),
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "enabled_afi": ["IPv4"],
                        }
                    ],
                }
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                interfaces += [i]

        # Last resort
        if not ipif_found:
            c = self.scripts.get_switch()
            i = {
                "name": "System",
                "type": "SVI",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [
                    {
                        "name": "System",
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            if self.is_des_a1:
                match = self.rx_ipif_des_a1.search(ipif)
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                v = self.cli("show management vlan")
                match = self.rx_mgmt_vlan.search(v)
                i["subinterfaces"][0]["vlan_ids"] = [match.group("vlan_id")]
                mac_address = self.rx_mac.search(c).group("mac")
                i["mac"] = mac_address
                i["subinterfaces"][0]["mac"] = mac_address
                interfaces += [i]

            match = self.rx_ipswitch.search(c)
            if match:
                mac_address = match.group("mac_address")
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                vlan_name = match.group("vlan_name")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                for v in vlans:
                    if vlan_name == v["vlan_name"]:
                        i["subinterfaces"][0]["vlan_ids"] = [v["vlan_id"]]
                        break
                i["mac"] = mac_address
                i["subinterfaces"][0]["mac"] = mac_address
                interfaces += [i]

        return [{"interfaces": interfaces}]
