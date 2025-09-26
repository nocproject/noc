# ---------------------------------------------------------------------
# Cisco.IOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import time
from collections import defaultdict
from itertools import compress, chain

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.base import InterfaceTypeError
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib
from noc.core.snmp.render import render_bin


class Script(BaseScript):
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
    interface = IGetInterfaces
    MAX_REPETITIONS = 15

    rx_sh_int = re.compile(
        r"^(?P<interface>.+?)\s+is(?:\s+administratively)?\s+(?P<admin_status>up|down),\s+line\s+"
        r"protocol\s+is\s+(?P<oper_status>up|down)\s?(?:\s+NOTE.+\n.+)?"
        r"(?:\((?:connected|notconnect|disabled|monitoring|err-disabled)\)\s*|, Autostate \S+)?\n"
        r"(^\s+Hardware is .+\n)?"
        r"\s+Hardware is (?P<hardw>[^\n]+)\n(?:\s+Description:\s(?P<desc>[^\n]+)\n)?"
        r"(?:\s+Internet address ((is\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}))|([^\d]+))\n)?"
        r"[^\n]+\n[^\n]+\n\s+Encapsulation\s+(?P<encaps>[^\n]+)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_sh_ip_int = re.compile(
        r"^(?P<interface>.+?)\s+is(?:\s+administratively)?\s+(?P<admin_status>up|down),\s+"
        r"line\s+protocol\s+is\s+",
        re.IGNORECASE,
    )
    rx_mac = re.compile(r"address\sis\s(?P<mac>\w{4}\.\w{4}\.\w{4})", re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(
        r"Internet address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_sec_ip = re.compile(
        r"Secondary address (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_ipv6 = re.compile(
        r"(?P<address>\S+), subnet is (?P<net>\S+)/(?P<mask>\d+)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_vlan_line = re.compile(
        r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+(?P<status>active|suspend|act\/unsup)\s+"
        r"(?P<ports>[\w\/\s\,\.]+)$",
        re.MULTILINE,
    )
    rx_vlan_line_cont = re.compile(r"^\s{10,}(?P<ports>[\w\/\s\,\.]+)$", re.MULTILINE)
    rx_ospf = re.compile(r"^(?P<name>\S+)\s+\d", re.MULTILINE)
    rx_pim = re.compile(r"^\S+\s+(?P<name>\S+)\s+v\d+/\S+\s+\d+")
    rx_igmp = re.compile(r"^(?P<name>\S+) is ")
    rx_cisco_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+(/\d+)?)?)?([.:]\d+(\.\d+)?)?(A|B)?)$",
        re.IGNORECASE,
    )
    rx_cisco_interface_sonet = re.compile(r"^(?P<type>Se)\s+(?P<number>\d+\S+)$")
    rx_ctp = re.compile(r"Keepalive set \(\d+ sec\)")
    rx_cdp = re.compile(r"^(?P<iface>\S+) is ")
    rx_lldp = re.compile(
        r"^(?P<iface>(?:Fa|Gi|Te|Fo|Fi|Tw|Twe)[^:]+?):.+Rx: (?P<rx_state>\S+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_gvtp = re.compile(r"VTP Operating Mode\s+: Off", re.MULTILINE)
    rx_vtp = re.compile(r"^\s*(?P<iface>(?:Fa|Gi|Te|Fo|Fi|Tw|Twe)[^:]+?)\s+enabled", re.MULTILINE)
    rx_vtp1 = re.compile(
        r"^\s*Local updater ID is \S+ on interface (?P<iface>(?:Fa|Gi|Te|Fo|Fi|Tw|Twe)[^:]+?)\s+",
        re.MULTILINE,
    )
    rx_oam = re.compile(r"^\s*(?P<iface>(?:Fa|Gi|Te|Fo)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s*$")

    rx_show_standby_brief = re.compile(
        r"(?P<iface>\S+)\s+(?P<group>\d+)\s+(?P<prior>\d+)\s+([P ])?\s+"
        r"(?P<status>\w+)\s+(?P<active_ip>[0-9.]+|local|standby|Active)\s+"
        r"(?P<standby_ip>[0-9.]+|local|standby)\s+(?P<virtual_ip>[0-9.]+)",
        re.MULTILINE,
    )
    rx_show_vrrp_brief = re.compile(
        r"(?P<iface>\S+)\s+(?P<group>\d+)\s+(?P<prior>\d+)\s+(?P<time>\d+)\s+(?P<own>\S+)?\s+(?P<pre>\w+)\s+"
        r"(?P<state>\w+)\s+(?P<master_addr>[0-9.]+|local|standby|Active|Master|Slave|Standby)\s+"
        r"(?P<virtual_ip>[0-9.]+)",
        re.MULTILINE,
    )

    def filter_interface(self, ifindex, name, oper_status):
        if name[:2] in ["Vi", "Di", "GM", "CP", "Nv", "Do", "Nu", "Co", "Em"]:
            return False
        # NOC-378 - Dirty hack for interface like ATM0/IMA0
        if "/ima" in name.lower():
            return False
        return True

    def get_lldp_interfaces(self):
        """
        Returns a set of normalized LLDP interface names
        :return:
        """
        try:
            v = self.cli("show lldp interface")
        except self.CLISyntaxError:
            return []
        r = []
        for s in v.strip().split("\n\n"):
            match = self.rx_lldp.search(s)
            if match:
                if match.group("rx_state").lower() == "enabled":
                    r += [self.profile.convert_interface_name(match.group("iface").strip())]
        return r

    def get_oam_interfaces(self):
        """
        Returns a set of normalized OAM interface names
        :return:
        """
        try:
            v = self.cli("show ethernet oam summary")
        except self.CLISyntaxError:
            return []
        r = []
        for s in v.strip().split("\n"):
            match = self.rx_oam.search(s)
            if match:
                r += [self.profile.convert_interface_name(match.group("iface").strip())]
        return r

    def get_cdp_interfaces(self):
        """
        Returns a set of normalized CDP interface names
        :return:
        """
        try:
            v = self.cli("show cdp interface")
        except self.CLISyntaxError:
            return []
        r = []
        for s in v.split("\n"):
            match = self.rx_cdp.search(s)
            if match:
                try:
                    r += [self.profile.convert_interface_name(match.group("iface").strip())]
                except InterfaceTypeError:
                    continue
        return r

    def get_vtp_interfaces(self):
        """
        Returns a set of normalized VTP interface names
        :return:
        """
        try:
            v = self.cli("show vtp status")
        except self.CLISyntaxError:
            return []
        if self.rx_gvtp.search(v):
            return []
        r = []
        try:
            v1 = self.cli("show vtp interface")
        except self.CLISyntaxError:
            v1 = v
        for s in v1.strip().split("\n"):
            match = self.rx_vtp.search(s)
            if match:
                r += [self.profile.convert_interface_name(match.group("iface").strip())]
            match = self.rx_vtp1.search(s)
            if match:
                r += [self.profile.convert_interface_name(match.group("iface").strip())]
        return r

    def get_ospfint(self):
        try:
            v = self.cli("show ip ospf interface brief")
        except self.CLISyntaxError:
            return []
        r = []
        for s in v.split("\n"):
            match = self.rx_ospf.search(s)
            if match:
                r += [match.group("name")]
        return r

    def get_pimint(self):
        try:
            v = self.cli("show ip pim interface")
        except self.CLISyntaxError:
            return []
        r = []
        for s in v.split("\n"):
            match = self.rx_pim.search(s)
            if match:
                r += [self.profile.convert_interface_name(match.group("name").strip())]
        return r

    def get_igmpint(self):
        try:
            v = self.cli("show ip igmp interface")
        except self.CLISyntaxError:
            return []
        r = []
        for s in v.split("\n"):
            match = self.rx_igmp.search(s)
            if match:
                r += [self.profile.convert_interface_name(match.group("name").strip())]
        return r

    rx_ifindex = re.compile(
        r"^(?P<interface>.+?)(?:-802\.1Q vLAN subif)?: Ifindex = (?P<ifindex>\d+)"
    )

    def get_ifindex(self):
        try:
            c = self.cli("show snmp mib ifmib ifindex")
        except self.CLISyntaxError:
            return {}
        r = {}
        for line in c.split("\n"):
            match = self.rx_ifindex.match(line.strip())
            if match:
                r[match.group("interface")] = int(match.group("ifindex"))
        return r

    # Cisco uBR7100, uBR7200, uBR7200VXR, uBR10000 Series
    rx_vlan_ubr = re.compile(r"^\w{4}\.\w{4}\.\w{4}\s(?P<port>\S+)\s+(?P<vlan_id>\d{1,4})")

    def get_ubr_pvm(self):
        vlans = self.cli("show cable l2-vpn dot1q-vc-map")
        pvm = {}
        for line in vlans.split("\n"):
            match = self.rx_vlan_ubr.search(line)
            if match:
                port = match.group("port")
                vlan_id = int(match.group("vlan_id"))
                if port not in pvm:
                    pvm[port] = ["%s" % vlan_id]
                else:
                    pvm[port] += ["%s" % vlan_id]
        return pvm

    def get_mpls_vpn(self):
        imap = {}  # interface -> VRF
        vrfs = {
            "default": {
                "forwarding_instance": "default",
                "type": "ip",
                "interfaces": [],
            }
        }
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            if v["type"] == "VRF":
                vrfs[v["name"]] = {
                    "forwarding_instance": v["name"],
                    "type": "VRF",
                    "interfaces": [],
                }
                rd = v.get("rd")
                if rd:
                    vrfs[v["name"]]["rd"] = rd
                vpn_id = v.get("vpn_id")
                if vpn_id:
                    vrfs[v["name"]]["vpn_id"] = vpn_id
                for i in v["interfaces"]:
                    imap[i] = v["name"]

        return vrfs, imap

    def get_switchport(self):
        result = defaultdict(lambda: {"tagged_vlans": [], "untagged_vlan": None})
        for oid, pvid in self.snmp.getnext(
            mib["CISCO-VLAN-MEMBERSHIP-MIB::vmVlan"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            timeout=self.get_snmp_timeout(),
        ):
            if not pvid:
                # if pvid is 0
                continue
            o = oid.split(".")[-1]
            result[int(o)]["untagged_vlan"] = pvid
        for (
            ifindex,
            native_vlan,
            enc_type,
            vlans_base,
            vlans_2k,
            vlans_3k,
            vlans_4k,
        ) in self.snmp.get_tables(
            [
                mib["CISCO-VTP-MIB::vlanTrunkPortNativeVlan"],
                mib["CISCO-VTP-MIB::vlanTrunkPortEncapsulationOperType"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled2k"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled3k"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled4k"]
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined"],
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined2k"],
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined3k"],
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined4k"],
            ],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            timeout=self.get_snmp_timeout(),
            display_hints={
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined"]: render_bin,
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined2k"]: render_bin,
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined3k"]: render_bin,
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined4k"]: render_bin,
            },
        ):
            # print(ifindex, enc_type, vlans_base, vlans_2k, vlans_3k, vlans_4k)
            if int(enc_type) != 4:
                # not dot1Q
                continue
            vlans_bank = b"".join([vlans_base, vlans_2k or b"", vlans_3k or b"", vlans_4k or b""])
            result[int(ifindex)]["tagged_vlans"] += list(
                compress(
                    range(0, 4096),
                    [
                        int(x)
                        for x in chain.from_iterable("{0:08b}".format(mask) for mask in vlans_bank)
                    ],
                )
            )
        time.sleep(2)
        return result

    def get_vrrp_interfaces(self):
        if not (
            self.has_capability("Network | VRRP | v2")
            or self.has_capability("Network | VRRP | v3")
            or self.has_capability("Network | HSRP")
        ):
            return {}
        vrrps = {}
        for cmd in ("show standby brief", "show vrrp brief"):
            try:
                v = self.cli(cmd)
            except self.CLISyntaxError:
                continue
            rx_vrrp = eval(f"self.rx_{cmd.replace(' ', '_')}")
            for match in rx_vrrp.finditer(v):
                ifname = self.profile.convert_interface_name(match.group("iface"))
                if ifname in vrrps:
                    vrrps[ifname] += [match.group("virtual_ip") + "/32"]
                else:
                    vrrps[ifname] = [match.group("virtual_ip") + "/32"]
        return vrrps

    def execute_cli(self):
        # Get port-to-vlan mappings
        pvm = {}
        switchports = {}  # interface -> (untagged, tagged)
        if self.is_ubr:
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
                for sp in self.scripts.get_switchport():
                    switchports[sp["interface"]] = (
                        sp["untagged"] if "untagged" in sp else None,
                        sp["tagged"],
                    )
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        # Get LLDP interfaces
        lldp = self.get_lldp_interfaces()
        # Get VTP interfaces
        vtp = self.get_vtp_interfaces()
        # Get OAM interfaces
        oam = self.get_oam_interfaces()
        # Get CDP interfaces
        cdp = self.get_cdp_interfaces()
        # Get IPv4 interfaces
        ipv4_interfaces = defaultdict(list)  # interface -> [ipv4 addresses]
        c_iface = None
        for line in self.cli("show ip interface").splitlines():
            match = self.rx_sh_ip_int.search(line)
            if match:
                c_iface = self.profile.convert_interface_name(match.group("interface").strip())
                continue
            # Primary ip
            match = self.rx_ip.search(line)
            if not match:
                # Secondary ip
                match = self.rx_sec_ip.search(line)
                if not match:
                    continue
            ip = match.group("ip")
            ipv4_interfaces[c_iface] += [ip]
        # Get IPv6 interfaces
        ipv6_interfaces = defaultdict(list)  # interface -> [ipv6 addresses]
        c_iface = None
        try:
            v = self.cli("show ipv6 interface")
        except self.CLISyntaxError:
            v = ""
        for line in v.splitlines():
            match = self.rx_sh_ip_int.search(line)
            if match:
                iface = match.group("interface")
                try:
                    c_iface = self.profile.convert_interface_name(iface).strip()
                except InterfaceTypeError:
                    c_iface = None
                continue
            if not c_iface:
                continue  # Skip wierd interfaces
            # Primary ip
            match = self.rx_ipv6.search(line)
            if not match:
                # Secondary ip?
                continue
            ip = "%s/%s" % (match.group("address"), match.group("mask"))
            ipv6_interfaces[c_iface] += [ip]
        interfaces = {}
        # Get OSPF interfaces
        ospfs = self.get_ospfint()
        # Get PIM interfaces
        pims = self.get_pimint()
        # Get IGMP interfaces
        igmps = self.get_igmpint()
        # Get interfaces SNMP ifIndex
        ifindex = self.get_ifindex()
        # Get VRRP interfaces
        vrrps = self.get_vrrp_interfaces()

        v = self.cli("show interface")
        for match in self.rx_sh_int.finditer(v):
            full_ifname = match.group("interface").strip()
            ifname = self.profile.convert_interface_name(full_ifname)
            if not self.filter_interface(0, ifname, True):
                continue
            if not self.filter_interface(0, full_ifname, True):
                continue
            if ":" in ifname:
                inm = ifname.split(":")[0]
                # Create root interface if not exists yet
                if inm not in interfaces:
                    iface = {
                        "name": inm,
                        "admin_status": True,
                        "oper_status": True,
                        "type": "physical",
                        "enabled_protocols": [],
                    }
                    if inm in lldp:
                        iface["enabled_protocols"] += ["LLDP"]
                    if inm in vtp:
                        iface["enabled_protocols"] += ["VTP"]
                    if inm in oam:
                        iface["enabled_protocols"] += ["OAM"]
                    if inm in cdp:
                        iface["enabled_protocols"] += ["CDP"]
                    interfaces[inm] = iface
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            hw = match.group("hardw")
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": [],
                "enabled_protocols": [],
            }
            if "alias" in match.groups():
                sub["description"] = match.group("alias")
            if match.group("desc"):
                sub["description"] = match.group("desc")
            matchmac = self.rx_mac.search(hw)
            if matchmac:
                sub["mac"] = matchmac.group("mac")
            if ifname in switchports and ifname not in portchannel_members:
                sub["enabled_afi"] += ["BRIDGE"]
                u, t = switchports[ifname]
                if u:
                    sub["untagged_vlan"] = u
                if t:
                    sub["tagged_vlans"] = t

            # Static vlans
            if match.group("encaps"):
                encaps = match.group("encaps")
                if encaps[:6] == "802.1Q":
                    sub["vlan_ids"] = [encaps.split(",")[1].split()[2].replace(".", "")]
            # uBR ?
            if ifname in pvm:
                sub["vlan_ids"] = pvm[ifname]
            # IPv4/Ipv6
            if match.group("ip"):
                if ifname in ipv4_interfaces:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = ipv4_interfaces[ifname]
                if ifname in ipv6_interfaces:
                    sub["enabled_afi"] += ["IPv6"]
                    sub["ipv6_addresses"] = ipv6_interfaces[ifname]
            matchifn = self.rx_cisco_interface_name.match(ifname)
            if not matchifn:
                matchifn = self.rx_cisco_interface_sonet.match(ifname)
            shotn = matchifn.group("type").capitalize() + matchifn.group("number")
            if shotn in ospfs:
                sub["enabled_protocols"] += ["OSPF"]
            if ifname in pims:
                sub["enabled_protocols"] += ["PIM"]
            if ifname in igmps:
                sub["enabled_protocols"] += ["IGMP"]
            if ifname in vrrps.keys():
                sub["enabled_protocols"] += ["VRRP"]
                sub["ipv4_addresses"] += vrrps[ifname]

            if full_ifname in ifindex:
                sub["snmp_ifindex"] = ifindex[full_ifname]

            if "." not in ifname and ":" not in ifname:
                iftype = self.profile.get_interface_type(ifname)
                if not iftype:
                    self.logger.info("Ignoring unknown interface type for: %s", ifname)
                    continue
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": iftype,
                    "enabled_protocols": [],
                    "subinterfaces": [sub],
                }
                if ifname in lldp:
                    iface["enabled_protocols"] += ["LLDP"]
                if ifname in vtp:
                    iface["enabled_protocols"] += ["VTP"]
                if ifname in oam:
                    iface["enabled_protocols"] += ["OAM"]
                if ifname in cdp:
                    iface["enabled_protocols"] += ["CDP"]
                match1 = self.rx_ctp.search(v)
                if match1:
                    iface["enabled_protocols"] += ["CTP"]
                if match.group("desc"):
                    iface["description"] = match.group("desc")
                if "mac" in sub:
                    iface["mac"] = sub["mac"]
                if "alias" in sub:
                    iface["alias"] = sub["alias"]
                # Set VLAN IDs for SVI
                if iface["type"] == "SVI":
                    sub["vlan_ids"] = [int(shotn[2:].strip())]
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["enabled_protocols"] += ["LACP"]
                # Ifindex
                if full_ifname in ifindex:
                    iface["snmp_ifindex"] = ifindex[full_ifname]
                interfaces[ifname] = iface
            else:
                # Append additional subinterface
                if ":" in ifname:
                    if_name, vlan_id = ifname.split(":", 1)
                else:
                    if_name, vlan_id = ifname.split(".", 1)
                try:
                    interfaces[if_name]["subinterfaces"] += [sub]
                except KeyError:
                    interfaces[if_name]["subinterfaces"] = [sub]

        # VRF and forwarding_instance proccessed
        vrfs, vrf_if_map = self.get_mpls_vpn_mappings()
        for i in interfaces.keys():
            iface_vrf = "default"
            subs = interfaces[i]["subinterfaces"]
            interfaces[i]["subinterfaces"] = []
            if i in vrf_if_map:
                iface_vrf = vrf_if_map[i]
                vrfs[vrf_if_map[i]]["interfaces"] += [interfaces[i]]
            else:
                vrfs["default"]["interfaces"] += [interfaces[i]]
            for s in subs:
                if s["name"] in vrf_if_map and vrf_if_map[s["name"]] != iface_vrf:
                    vrfs[vrf_if_map[s["name"]]]["interfaces"] += [
                        {
                            "name": s["name"],
                            "type": "other",
                            "enabled_protocols": [],
                            "subinterfaces": [s],
                        }
                    ]
                else:
                    interfaces[i]["subinterfaces"] += [s]
        return list(vrfs.values())
