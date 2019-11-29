# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import time

# Third-party modules
import six

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


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

    rx_phys = re.compile(r"\S+\sinterface:\s(?P<ifname>\S+)\s*,\s", re.MULTILINE)
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
        r"^\s+Flags:.+VLAN-Tag \[\s*0x\d+\.(?P<vlan>\d+)" r"(\s+0x\d+\.(?P<vlan2>\d+))?\s*\]",
        re.MULTILINE,
    )
    # Flags: Up SNMP-Traps 0x20004000 \
    #   VLAN-Tag [ 0x8100.3637 0x8100.19 ] In(pop-swap .999) Out(swap-push 0x8100.3637 .19)
    rx_flags_unnumbered = re.compile(r"^\s+Flags:.+, Unnumbered", re.MULTILINE)
    rx_iface_unnumbered = re.compile(r"^\s+Donor interface: (?P<name>\S+)", re.MULTILINE)
    rx_mtu = re.compile(r", MTU: (?P<mtu>\d+)")
    # IP-Header 172.17.1.6:172.17.1.1:47:df:64:0000000000000000
    rx_ppp_address = re.compile(r"IP-Header (?P<src>\S+?):(?P<dst>\S+?):(?P<proto>\d+)")
    rx_ri = re.compile(
        r"(?P<name>\S+?):\n"
        r"(?:  Description: (?P<description>.+?)\n)?"
        r"  Router ID: (?P<router_id>\S+)\n"
        r"  Type: (?P<type>\S+)\s+\S*\s+State:\s+(?P<status>Active|Inactive)\s*\n"
        r"  Interfaces:\n"
        r"(?P<ifaces>(?:    \S+\n)*)"
        r"(  Route-distinguisher: (?P<rd>\S+)\s*\n)?"
        r"(  Vrf-import: \[(?P<vrf_import>.+)\]\s*\n)?"
        r"(  Vrf-export: \[(?P<vrf_export>.+)\]\s*\n)?",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_vrf_target = re.compile(r"target:(?P<rd>\d+:\d+)")
    type_map = {
        "virtual-router": "ip",
        "vrf": "VRF",
        "vpls": "VPLS",
        "l2vpn": "VLL",
        "evpn": "EVPN",
    }

    def get_vrf(self):
        c = self.cli(
            'help apropos "instance" | match "^show route instance" ',
            cached=True,
            ignore_errors=True,
        )
        if "show route instance" not in c:
            return []

        vpns = []
        v = self.cli("show route instance detail")
        for match in self.rx_ri.finditer(v):
            name = match.group("name")
            rt = match.group("type").lower()
            if name == "master" or name.startswith("__") or rt not in self.type_map:
                continue
            interfaces = [x.strip() for x in match.group("ifaces").splitlines()]
            interfaces = [x for x in interfaces if x and not x.startswith("lsi.")]
            vpn = {
                "type": self.type_map[rt],
                "virtual_router": match.group("router_id"),
                "status": match.group("status").lower() == "active",
                "name": name,
                "rd": match.group("rd"),
                "interfaces": interfaces,
            }
            description = match.group("description")
            if description:
                vpn["description"] = description.strip()
            if match.group("vrf_import"):
                vpn["rt_import"] = []
                for rt_name in match.group("vrf_import").split(" "):
                    rt_name = rt_name.strip()
                    if rt_name == "":
                        continue
                    if rt_name.startswith("target:"):
                        vpn["rt_import"] += [rt_name[7:]]
                    c = self.cli("show policy %s" % rt_name)
                    for rd in self.rx_vrf_target.finditer(c):
                        vpn["rt_import"] += [rd.group("rd")]
            if match.group("vrf_export"):
                vpn["rt_export"] = []
                for rt_name in match.group("vrf_export").split(" "):
                    rt_name = rt_name.strip()
                    if rt_name == "":
                        continue
                    if rt_name.startswith("target:"):
                        vpn["rt_export"] += [rt_name[7:]]
                    c = self.cli("show policy %s" % rt_name)
                    for rd in self.rx_vrf_target.finditer(c):
                        vpn["rt_export"] += [rd.group("rd")]
            vpns += [vpn]
        return vpns

    def execute_cli(self):
        untagged = {}
        tagged = {}
        l3_ids = {}
        vlans_requested = False
        interfaces = {}
        ifaces = []

        q = self.cli("show interfaces media | match interface:")
        ifaces = self.rx_phys.findall(q)

        for iface in ifaces:
            v = self.cli("show interfaces %s" % iface)
            L = self.rx_log_split.split(v)
            phy = L.pop(0)
            phy = phy.replace(" )", "")
            match = self.rx_phy_name.search(phy)
            name = match.group("ifname")
            if name.endswith(")"):
                name = name[:-1]
            if not self.profile.valid_interface_name(self, name):
                continue
            # Detect interface type
            if name.startswith("lo"):
                iftype = "loopback"
            elif name.startswith(("fxp", "me")):
                iftype = "management"
            elif name.startswith(("ae", "reth", "fab", "swfab")):
                iftype = "aggregated"
            elif name.startswith(("vlan", "vme")):
                iftype = "SVI"
            elif name.startswith("irb"):
                iftype = "SVI"
            elif name.startswith(("fc", "fe", "ge", "xe", "sxe", "xle", "et", "fte")):
                iftype = "physical"
            elif name.startswith(("gr", "ip", "st")):
                iftype = "tunnel"
            elif name.startswith("em"):
                if self.is_work_em:
                    iftype = "physical"
                else:
                    iftype = "management"
            else:
                iftype = "unknown"

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
                iface["description"] = match.group("description").decode("ascii", "ignore")
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
                    si["description"] = match.group("description").decode("ascii", "ignore")
                # Get vlans
                vlan_ids = []
                match = self.rx_flags_vlan.search(s)
                if match:
                    # Skip like this

                    #  Logical interface ge-0/0/13.0 (Index 143) (SNMP ifIndex 551)
                    #    Flags: Up 0x0 VLAN-Tag [ 0x0000.0 ]  Encapsulation: ENET2
                    #    Protocol aenet, AE bundle: ae0.0

                    if int(match.group("vlan")) != 0:
                        vlan_ids = [int(match.group("vlan"))]
                    if match.group("vlan2") and int(match.group("vlan2")) != 0:
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
                            ):
                                v = self.cli("show vlans detail")
                                untagged, tagged, l3_ids = self.get_vlan_port_mapping(v)
                                if not l3_ids:
                                    # Found in ex4500, Junos: 15.1R7.8
                                    v = self.cli("show vlans extensive")
                                    untagged1, tagged1, l3_ids = self.get_vlan_port_mapping(v)
                            vlans_requested = True
                        if untagged.get(si["name"]):
                            si["untagged_vlans"] = untagged[si["name"]]
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
        # Process VRFs
        vrfs = {"default": {"forwarding_instance": "default", "type": "ip", "interfaces": []}}
        imap = {}  # interface -> VRF
        r = self.get_vrf()
        for v in r:
            vrfs[v["name"]] = {
                "forwarding_instance": v["name"],
                "virtual_router": v["virtual_router"],
                "type": v["type"],
                "vpn_id": v.get("vpn_id"),
                "interfaces": [],
            }
            rd = v.get("rd")
            if rd:
                vrfs[v["name"]]["rd"] = rd
            for i in v["interfaces"]:
                imap[i] = v["name"]
        for i in interfaces.keys():
            iface_vrf = "default"
            subs = interfaces[i]["subinterfaces"]
            interfaces[i]["subinterfaces"] = []
            if i in imap:
                iface_vrf = imap[i]
                vrfs[imap[i]]["interfaces"] += [interfaces[i]]
            else:
                vrfs["default"]["interfaces"] += [interfaces[i]]
            for s in subs:
                if s["name"] in imap and imap[s["name"]] != iface_vrf:
                    vrfs[imap[s["name"]]]["interfaces"] += [
                        {
                            "name": s["name"],
                            "type": "other",
                            "enabled_protocols": [],
                            "subinterfaces": [s],
                        }
                    ]
                else:
                    interfaces[i]["subinterfaces"] += [s]
        return list(six.itervalues(vrfs))

    rx_vlan_sep = re.compile(r"^VLAN:", re.MULTILINE)
    rx_802_1Q_tag = re.compile(r"802.1Q\s+Tag:\s+(?P<tag>\d+)", re.IGNORECASE | re.MULTILINE)
    rx_vlan_untagged = re.compile(r"\s+Untagged interfaces:\s*(.+)", re.MULTILINE | re.DOTALL)
    rx_vlan_tagged = re.compile(r"\s+Tagged interfaces:\s*(.+)", re.MULTILINE | re.DOTALL)

    rx_vlan_sep1 = re.compile(r"^\nRouting instance:", re.MULTILINE)
    rx_802_1Q_tag1 = re.compile(r"^Tag:\s+(?P<tag>\d+)", re.MULTILINE)
    rx_l3_iface = re.compile(r"^Layer 3 interface: (?P<iface>\S+)", re.MULTILINE)
    rx_iface_vlan = re.compile(r"^\s+(?P<iface>\S\S\-\S+),(?P<type>tagged|untagged)", re.MULTILINE)

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
