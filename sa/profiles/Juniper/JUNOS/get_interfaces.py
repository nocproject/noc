# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    """
    Juniper.JUNOS.get_interfaces

    @todo: virtual routers
    @todo: vrfs
    @todo: vlan ids of the units
    """
    name = "Juniper.JUNOS.get_interfaces"
    implements = [IGetInterfaces]

    rx_phy_split = re.compile(r"^Physical interface:\s+", re.MULTILINE)
    rx_phy_name = re.compile(r"^(?P<ifname>\S+), (?P<admin>Enabled|Disabled|Administratively down), Physical link is (?P<oper>Up|Down)",
                             re.MULTILINE | re.IGNORECASE)
    rx_phy_description = re.compile(r"^\s+Description:\s+(?P<description>.+?)\s*$",
                                    re.MULTILINE)
    rx_phy_ifindex = re.compile(r"SNMP ifIndex: (?P<ifindex>\d+)",
                                re.MULTILINE | re.IGNORECASE)
    rx_phy_mac = re.compile(r"^\s+Current address: (?P<mac>\S+),", re.MULTILINE)
    rx_log_split = re.compile(r"^\s+Logical interface\s+", re.MULTILINE)
    rx_log_name = re.compile(r"^(?P<name>\S+).+?SNMP ifIndex (?P<ifindex>\d+)",
                             re.IGNORECASE)
    rx_log_protocol = re.compile(r"^\s+Protocol\s+", re.MULTILINE)
    rx_log_pname = re.compile(r"^(?P<proto>[a-zA-Z0-9\-]+)")
    rx_log_address = re.compile(r"^\s+Local:\s+(?P<address>\S+)", re.MULTILINE)
    rx_log_netaddress = re.compile(r"^\s+Destination: (?P<dest>\S+?),\s+Local: (?P<local>\S+?),",
        re.MULTILINE)
    rx_log_netaddress6 = re.compile(r"^\s+Destination: (?P<dest>\S+?),[ \r\n]+Local: (?P<local>\S+?)$",
        re.MULTILINE)
    rx_log_ae = re.compile(r"AE bundle: (?P<bundle>\S+?)\.\d+", re.MULTILINE)
    rx_flags_vlan = re.compile(r"^\s+Flags:.+VLAN-Tag \[\s*0x\d+\.(?P<vlan>\d+)\s*\]",
        re.IGNORECASE | re.MULTILINE)

    internal_interfaces = re.compile(r"^(lc-|cbp|demux|dsc|em|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip|bme|jsrv|pfe|pfh|vcp|mt-|pd|pe|vt-|vtep)")
    internal_interfaces_olive = re.compile(r"^(lc-|cbp|demux|dsc|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip)")

    def execute(self):
        untagged = {}
        tagged = {}
        vlans_requested = False
        interfaces = []
        version = self.scripts.get_version()
        if version["platform"] == "olive":
            internal = self.internal_interfaces_olive
        else:
            internal = self.internal_interfaces
        v = self.cli("show interfaces")
        for I in self.rx_phy_split.split(v)[1:]:
            L = self.rx_log_split.split(I)
            phy = L.pop(0)
            match = self.re_search(self.rx_phy_name, phy)
            name = match.group("ifname")
            # Skip internal interfaces
            if internal.search(name):
                continue
            # Detect interface type
            if name.startswith("lo"):
                iftype = "loopback"
            elif name.startswith("fxp"):
                iftype = "management"
            elif name.startswith("ae") or name.startswith("reth"):
                iftype = "aggregated"
            elif name.startswith("vlan"):
                iftype = "SVI"
            else:
                iftype = "physical"
            # Get interface parameters
            iface = {
                "name": name,
                "admin_status": match.group("admin").lower() == "enabled",
                "oper_status": match.group("oper").lower() == "up",
                "type": iftype,
                }
            # Get description
            match = self.rx_phy_description.search(phy)
            if match:
                iface["description"] = match.group("description")
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
            # Process subinterfaeces
            subs = []
            for s in L:
                match = self.re_search(self.rx_log_name, s)
                sname = match.group("name")
                si = {
                    "name": sname,
                    "snmp_ifindex": match.group("ifindex"),
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": []
                }
                if mac:
                    si["mac"] = mac
                # Get description
                match = self.rx_phy_description.search(s)
                if match:
                    si["description"] = match.group("description")
                # Get vlans
                vlan_ids = []
                match = self.rx_flags_vlan.search(s)
                if match:
                    vlan_ids = [int(match.group("vlan"))]
                # Process protocols
                for p in self.rx_log_protocol.split(s)[1:]:
                    match = self.re_search(self.rx_log_pname, p)
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
                        si["ipv4_addresses"] = ["%s/32" % a for a in
                                                local_addresses]
                        # Find connected networks
                        for match in self.rx_log_netaddress.finditer(p):
                            net, addr = match.groups()
                            n, m = net.split("/")
                            si["ipv4_addresses"] += ["%s/%s" % (addr, m)]
                    elif proto == "inet6":
                        # Protocol IPv6
                        si["enabled_afi"] += ["IPv6"]
                        si["ipv6_addresses"] = ["%s/128" % a for a in
                                                local_addresses]
                        # Find connected networks
                        for match in self.rx_log_netaddress6.finditer(p):
                            net, addr = match.groups()
                            n, m = net.split("/")
                            si["ipv6_addresses"] += ["%s/%s" % (addr, m)]
                    elif proto == "aenet":
                        # Aggregated
                        match = self.re_search(self.rx_log_ae, p)
                        bundle = match.group("bundle")
                        iface["aggregated_interface"] = bundle
                    elif proto.lower() == "eth-switch":
                        if not vlans_requested:
                            # Request vlans port mapping
                            untagged, tagged = self.get_vlan_port_mapping()
                            vlans_requested = True
                        # Set untagged
                        try:
                            si["untagged_vlans"] = untagged[si["name"]]
                        except KeyError:
                            pass
                        # Set tagged
                        try:
                            si["tagged_vlans"] = sorted(tagged[si["name"]])
                        except KeyError:
                            pass
                        # x = untagged.get(si["name"])
                        # if x:
                        #     si["untagged_vlans"]
                    # Set vlan_ids
                    if vlan_ids and (
                        "IPv4" in si["enabled_afi"] or
                        "IPv6" in si["enabled_afi"]):
                        si["vlan_ids"] = vlan_ids
                # Append to subinterfaces list
                subs += [si]
            # Append to collected interfaces
            iface["subinterfaces"] = subs
            interfaces += [iface]
        # Process VRFs
        vrfs = {
            "default": {
                "forwarding_instance": "default",
                "type": "ip",
                "interfaces": []
            }
        }
        imap = {}  # interface -> VRF
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            if v["type"] == "VRF":
                vrfs[v["name"]] = {
                    "forwarding_instance": v["name"],
                    "type": "VRF",
                    "rd": v["rd"],
                    "interfaces": []
                }
                for i in v["interfaces"]:
                    imap[i] = v["name"]
        for i in interfaces:
            subs = i["subinterfaces"]
            for vrf in set(imap.get(si["name"], "default") for si in subs):
                c = i.copy()
                c["subinterfaces"] = [si for si in subs
                                      if imap.get(si["name"], "default") == vrf]
                vrfs[vrf]["interfaces"] += [c]
        return vrfs.values()


    rx_vlan_sep = re.compile(r"^VLAN:", re.MULTILINE)
    rx_802_1Q_tag = re.compile(r"802.1Q\s+Tag:\s+(?P<tag>\d+)",
                               re.IGNORECASE | re.MULTILINE)
    rx_vlan_untagged = re.compile(r"\s+Untagged interfaces:\s*(.+)",
                                  re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_vlan_tagged = re.compile(r"\s+Tagged interfaces:\s*(.+)",
                                re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def get_vlan_port_mapping(self):
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
            o = s
            s = s.strip()
            if s.endswith("*"):
                s = s[:-1]
            if s.lower() == "none":
                s = ""
            return s

        untagged = {}  # port -> vlan id
        tagged = {}  # port -> [vlan_id, ...]
        v = self.cli("show vlans detail")
        for vdata in self.rx_vlan_sep.split(v):
            match = self.rx_802_1Q_tag.search(vdata)
            if match:
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
                    vdata = vdata[:match.start()]
                # Process untagged interfaces
                match = self.rx_vlan_untagged.search(vdata)
                if match:
                    for i in match.group(1).split(","):
                        i = clean_interface(i)
                        if i:
                            untagged[i] = tag
                continue
            # @todo: Q-in-Q handling
        self.debug("VLANS: %s %s" % (untagged, tagged))
        return untagged, tagged
