# ---------------------------------------------------------------------
# Juniper.JUNOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import time

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.comp import smart_text
from noc.core.validators import is_vlan


class Script(BaseScript):
    """
    Juniper.JUNOS.get_interfaces

    @todo: virtual routers
    @todo: vrfs
    @todo: vlan ids of the units
    """

    name = "Juniper.JUNOS.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 240
    BULK = False

    rx_phys = re.compile(r"\S+\sinterface:\s(?P<ifname>\S+)(?: \(\S+, \S+\))?\s*, ", re.MULTILINE)
    rx_phy_name = re.compile(
        r"^Physical interface: (?P<ifname>\S+)"
        r"( \(\S+, \S+\))?( \(Extended Port)?\s*, "
        r"(?P<admin>Enabled|Disabled|Administratively down), "
        r"Physical link is (?P<oper>Up|Down)",
        re.MULTILINE,
    )
    rx_phy_description = re.compile(r"^\s+Description:\s+(?P<description>.+?)\s*$", re.MULTILINE)
    rx_phy_ifindex = re.compile(r"SNMP ifIndex: (?P<ifindex>\d+)")
    # # Do not match 'Unspecified'
    rx_phy_mac = re.compile(
        r"^\s+Current address: (?P<mac>([0-9A-Fa-f]{2}\:){5}[0-9A-Fa-f]{2}),", re.MULTILINE
    )
    rx_log_split = re.compile(r"^\s+Logical interface\s+", re.MULTILINE)
    rx_log_name = re.compile(r"^(?P<name>\S+).+?SNMP ifIndex (?P<ifindex>\d+)", re.MULTILINE)
    rx_log_protocol = re.compile(r"^\s+Protocol\s+", re.MULTILINE)
    rx_log_pname = re.compile(r"^(?P<proto>[a-zA-Z0-9\-]+)", re.MULTILINE)
    rx_log_address = re.compile(r"^\s+Local:\s+(?P<address>\S+)", re.MULTILINE)
    rx_log_netaddress = re.compile(
        r"^\s+Destination: (?P<dest>\S+?),\s+Local: (?P<local>\S+?)(?:,|$)", re.MULTILINE
    )
    rx_log_netaddress6 = re.compile(
        r"^\s+Destination: (?P<dest>\S+?),[ \r\n]+Local: (?P<local>\S+?)$", re.MULTILINE
    )
    rx_log_ae = re.compile(r"AE bundle: (?P<bundle>\S+?)\.\d+")
    rx_flags_vlan = re.compile(
        r"^\s+Flags:.+VLAN-Tag \[\s*0x\d+\.(?P<vlan>\d+)(\s+0x\d+\.(?P<vlan2>\d+))?\s*\]",
        re.MULTILINE,
    )
    # Flags: Up SNMP-Traps 0x20004000 \
    #   VLAN-Tag [ 0x8100.3637 0x8100.19 ] In(pop-swap .999) Out(swap-push 0x8100.3637 .19)
    rx_flags_unnumbered = re.compile(r"^\s+Flags:.+, Unnumbered", re.MULTILINE)
    rx_iface_unnumbered = re.compile(r"^\s+Donor interface: (?P<name>\S+)", re.MULTILINE)
    rx_mtu = re.compile(r", MTU: (?P<mtu>\d+)")
    # IP-Header 172.17.1.6:172.17.1.1:47:df:64:0000000000000000
    rx_ppp_address = re.compile(r"IP-Header (?P<src>\S+?):(?P<dst>\S+?):(?P<proto>\d+)")

    def filter_interface(self, ifindex, name, oper_status):
        if not self.profile.valid_interface_name(self, name):
            return False
        return True

    def clean_iftype(self, ifname: str, ifindex=None) -> str:
        if self.is_srx_6xx and ifname.startswith("reth"):
            return "physical"
        elif self.is_work_em and ifname.startswith("em"):
            return "physical"
        return self.profile.get_interface_type(ifname)

    def execute_cli(self):
        untagged = {}
        tagged = {}
        l3_ids = {}
        vlans_requested = False
        interfaces = {}
        ifaces = []

        v = self.cli("show interfaces media | match interface:")
        ifaces = self.rx_phys.findall(v)

        for iface in ifaces:
            if not self.filter_interface(0, iface, True):
                continue
            v = self.cli("show interfaces %s" % iface)
            L = self.rx_log_split.split(v)
            phy = L.pop(0)
            phy = phy.replace(" )", "")
            match = self.rx_phy_name.search(phy)
            name = match.group("ifname")
            if name.endswith(")"):
                name = name[:-1]
            # Do not remove, additional verification
            if not self.filter_interface(0, name, True):
                continue
            # Detect interface type
            iftype = self.clean_iftype(name)
            # Get interface parameters
            iface = {
                "name": name,
                "admin_status": match.group("admin").lower() == "enabled",
                "oper_status": match.group("oper").lower() == "up",
                "type": iftype,
            }
            def_si = {
                "name": name,
                "admin_status": match.group("admin").lower() == "enabled",
                "oper_status": match.group("oper").lower() == "up",
            }
            # Get description
            match = self.rx_phy_description.search(phy)
            if match and match.group("description") != "-=unused=-":
                iface["description"] = smart_text(
                    match.group("description"), errors="ignore", encoding="ascii"
                )
            # Get ifindex
            match = self.rx_phy_ifindex.search(phy)
            if match:
                iface["snmp_ifindex"] = match.group("ifindex")
            # Get MAC
            mac = None
            match = self.rx_phy_mac.search(phy)
            if match:
                mac = match.group("mac")
                iface["mac"] = mac
                def_si["mac"] = mac
            match = self.rx_mtu.search(phy)
            if match:
                def_si["mtu"] = match.group("mtu")
            # Process subinterfaeces
            subs = []
            for s in L:
                match = self.rx_log_name.search(s)
                sname = match.group("name")
                if not self.profile.valid_interface_name(self, sname):
                    continue
                si = {
                    "name": sname,
                    "snmp_ifindex": match.group("ifindex"),
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": [],
                }
                if mac:
                    si["mac"] = mac
                # Get MTU
                match = self.rx_mtu.search(s)
                if match:
                    si["mtu"] = match.group("mtu")
                # Get description
                match = self.rx_phy_description.search(s)
                if match:
                    si["description"] = smart_text(
                        match.group("description"), errors="ignore", encoding="ascii"
                    )
                # Get vlans
                vlan_ids = []
                match = self.rx_flags_vlan.search(s)
                if match:
                    # Skip like this

                    #  Logical interface ge-0/0/13.0 (Index 143) (SNMP ifIndex 551)
                    #    Flags: Up 0x0 VLAN-Tag [ 0x0000.0 ]  Encapsulation: ENET2
                    #    Protocol aenet, AE bundle: ae0.0

                    if is_vlan(match.group("vlan")):
                        vlan_ids = [int(match.group("vlan"))]
                    if match.group("vlan2") and is_vlan(match.group("vlan2")):
                        vlan_ids += [int(match.group("vlan2"))]
                # `irb` and `vlan` interfaces display other,
                # then `eth-switch` protocol
                if l3_ids.get(sname):
                    vlan_ids = [l3_ids[sname]]
                # Process protocols
                for p in self.rx_log_protocol.split(s)[1:]:
                    match = self.rx_log_pname.search(p)
                    proto = match.group("proto")
                    local_addresses = self.rx_log_address.findall(p)
                    if proto == "iso":
                        # Protocol ISO
                        si["enabled_afi"] += ["ISO"]
                        if local_addresses:
                            si["iso_addresses"] = local_addresses
                    elif proto == "mpls":
                        # MPLS protocol
                        si["enabled_afi"] += ["MPLS"]
                    elif proto == "inet":
                        # Protocol IPv4
                        si["enabled_afi"] += ["IPv4"]
                        si["ipv4_addresses"] = ["%s/32" % a for a in local_addresses]
                        # Find connected networks
                        for match in self.rx_log_netaddress.finditer(p):
                            net, addr = match.groups()
                            n, m = net.split("/")
                            si["ipv4_addresses"] += ["%s/%s" % (addr, m)]
                    elif proto == "inet6":
                        # Protocol IPv6
                        si["enabled_afi"] += ["IPv6"]
                        si["ipv6_addresses"] = ["%s/128" % a for a in local_addresses]
                        # Find connected networks
                        for match in self.rx_log_netaddress6.finditer(p):
                            net, addr = match.groups()
                            n, m = net.split("/")
                            si["ipv6_addresses"] += ["%s/%s" % (addr, m)]
                    elif proto == "aenet":
                        # Aggregated
                        match = self.rx_log_ae.search(p)
                        if match:
                            bundle = match.group("bundle")
                            iface["aggregated_interface"] = bundle
                    elif proto.lower() == "eth-switch" or proto.lower() == "multiservice":
                        if proto.lower() == "eth-switch":
                            si["enabled_afi"] += ["BRIDGE"]
                        if not vlans_requested:
                            if self.is_switch and (
                                self.profile.command_exist(self, "vlans")
                                or self.profile.command_exist(self, "vlan")
                                or not self.is_cli_help_supported
                            ):
                                v = self.cli("show vlans detail")
                                untagged, tagged, l3_ids = self.get_vlan_port_mapping(v)
                                if not l3_ids:
                                    # Found in ex4500, Junos: 15.1R7.8
                                    v = self.cli("show vlans extensive")
                                    untagged1, tagged1, l3_ids = self.get_vlan_port_mapping(v)
                            vlans_requested = True
                        if untagged.get(si["name"]):
                            si["untagged_vlan"] = untagged[si["name"]]
                        if tagged.get(si["name"]):
                            si["tagged_vlans"] = sorted(tagged[si["name"]])
                        # Set vlan_ids for EX series
                        if l3_ids.get(si["name"]):
                            si["vlan_ids"] = [l3_ids[si["name"]]]
                        # x = untagged.get(si["name"])
                        # if x:
                        #     si["untagged_vlans"]
                    """
                    Why we are setting vlan_ids only on IP interfaces ?

                    # Set vlan_ids
                    if vlan_ids and (
                        "IPv4" in si["enabled_afi"] or
                        "IPv6" in si["enabled_afi"]
                    ):
                        si["vlan_ids"] = vlan_ids
                    """
                    if vlan_ids:
                        si["vlan_ids"] = vlan_ids
                if self.rx_flags_unnumbered.search(s):
                    match = self.rx_iface_unnumbered.search(s)
                    if match:
                        si["ip_unnumbered_subinterface"] = match.group("name")
                # Get tunnel type
                if iface["type"] == "tunnel":
                    si["tunnel"] = {}
                    if sname.startswith("ip"):
                        si["tunnel"]["type"] = "IPIP"
                    elif sname.startswith("st"):
                        si["tunnel"]["type"] = "IPsec"
                    elif sname.startswith("gr"):
                        si["tunnel"]["type"] = "GRE"
                        match = self.rx_ppp_address.search(s)
                        if match and int(match.group("proto")) == 47:  # GRE
                            si["tunnel"]["local_address"] = match.group("src")
                            si["tunnel"]["remote_address"] = match.group("dst")
                    else:
                        raise self.NotSupportedError("Unknown tunnel type")
                # Append to subinterfaces list
                subs += [si]
            if not subs:
                subs += [def_si]
            # Append to collected interfaces
            iface["subinterfaces"] = subs
            interfaces[name] = iface
            time.sleep(1)
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

    rx_vlan_sep = re.compile(r"^VLAN:", re.MULTILINE)
    rx_802_1Q_tag = re.compile(r"802.1Q\s+Tag:\s+(?P<tag>\d+)", re.IGNORECASE | re.MULTILINE)
    rx_vlan_untagged = re.compile(r"\s+Untagged interfaces:\s*(.+)", re.MULTILINE | re.DOTALL)
    rx_vlan_tagged = re.compile(r"\s+Tagged interfaces:\s*(.+)", re.MULTILINE | re.DOTALL)

    # Routing instance: default-switch
    # VLAN Name: v0552                          State: Active
    # Tag: 552
    # Internal index: 654, Generation Index: 655, Origin: Static
    # MAC aging time: 300 seconds
    # VXLAN Enabled : No
    # Interfaces:
    #    ae1.0*,tagged,trunk
    #    xe-0/0/7.0*,tagged,trunk
    # Number of interfaces: Tagged 2    , Untagged 0
    # Total MAC count: 2
    rx_vlan_sep1 = re.compile(r"^\nRouting instance:", re.MULTILINE)
    rx_802_1Q_tag1 = re.compile(r"^Tag:\s+(?P<tag>\d+)", re.MULTILINE)
    rx_l3_iface = re.compile(r"^Layer 3 interface: (?P<iface>\S+)", re.MULTILINE)
    rx_iface_vlan = re.compile(r"^\s+(?P<iface>\S+),(?P<type>tagged|untagged)", re.MULTILINE)

    def get_vlan_port_mapping(self, v):
        """
        Get Vlan to port mappings for Juniper EX series.
        Returns two dicts: port -> untagged vlan, port -> tagged vlans
        :return: tagged map, untagged map
        :rtype: tuple
        """

        def clean_interface(s):
            """
            Clean interface name
            :param s: Interface name
            :returns: Cleaned interface name
            """
            s = s.strip()
            if s.endswith("*"):
                s = s[:-1]
            if s.lower() == "none":
                s = ""
            return s

        untagged = {}  # port -> vlan id
        tagged = {}  # port -> [vlan_id, ...]
        l3_ids = {}  # port -> vlan_id
        # v = self.cli("show vlans detail")
        found = False
        for vdata in self.rx_vlan_sep.split(v):
            match = self.rx_802_1Q_tag.search(vdata)
            if match:
                found = True
                # 802.1Q VLAN
                tag = int(match.group("tag"))
                # Process tagged interfaces
                match = self.rx_vlan_tagged.search(vdata)
                if match:
                    for i in match.group(1).split(","):
                        i = clean_interface(i)
                        try:
                            tagged[i] += [tag]
                        except KeyError:
                            tagged[i] = [tag]
                    vdata = vdata[: match.start()]
                # Process untagged interfaces
                match = self.rx_vlan_untagged.search(vdata)
                if match:
                    for i in match.group(1).split(","):
                        i = clean_interface(i)
                        if i:
                            untagged[i] = tag
                match = self.rx_l3_iface.search(vdata)
                if match:
                    i = match.group("iface")
                    i = clean_interface(i)
                    l3_ids[i] = tag
        if found:
            # self.logger.debug("VLANS: %s %s" % (untagged, tagged))
            return untagged, tagged, l3_ids
        for vdata in self.rx_vlan_sep1.split(v):
            match = self.rx_802_1Q_tag1.search(vdata)
            if match:
                # 802.1Q VLAN
                tag = int(match.group("tag"))
                # Process interfaces
                for match in self.rx_iface_vlan.finditer(vdata):
                    i = match.group("iface")
                    i = clean_interface(i)
                    if match.group("type") == "tagged":
                        try:
                            tagged[i] += [tag]
                        except KeyError:
                            tagged[i] = [tag]
                    else:
                        untagged[i] = tag
                match = self.rx_l3_iface.search(vdata)
                if match:
                    i = match.group("iface")
                    i = clean_interface(i)
                    l3_ids[i] = tag
        # self.logger.debug("VLANS: %s %s %s" % (untagged, tagged, l3_ids))
        # @todo: Q-in-Q handling
        return untagged, tagged, l3_ids
