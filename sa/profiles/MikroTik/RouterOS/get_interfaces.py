# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_interfaces"
    interface = IGetInterfaces

    type_map = {
        "ether": "physical",
        "wlan": "physical",
        "bridge": "SVI",
        "vlan": "SVI",
        "ppp-out": "tunnel",
        "ppp-in": "tunnel",
        "pppoe-out": "tunnel",
        "pppoe-in": "tunnel",
        "l2tp-out": "tunnel",
        "l2tp-in": "tunnel",
        "pptp-out": "tunnel",
        "pptp-in": "tunnel",
        "ovpn-out": "tunnel",
        "ovpn-in": "tunnel",
        "sstp-out": "tunnel",
        "sstp-in": "tunnel",
        "gre-tunnel": "tunnel",
        "ipip-tunnel": "tunnel",
        "ipip": "tunnel",
        "eoip": "tunnel",
        "eoip-tunnel": "tunnel",
        "bond": "aggregated"
    }

    ignored_types = set([
        "mesh", "traffic-eng", "vpls", "vrrp", "wds", "lte",
        "cap", "vrrp", "vif"
    ])
    si = {}

    def get_tunnel(self, tun_type, f, afi, ipif):
        self.si["tunnel"] = {}
        tun = self.si["tunnel"]
        tun["type"] = tun_type
        if tun_type in ["PPP", "PPPOE", "L2TP", "PPTP", "OVPN", "SSTP"]:
            if (f == "D" and afi == "IPv4"):
                tun["local_address"] = ipif["address"].split("/", 1)[0].strip()
                tun["remote_address"] = ipif["network"]
                return
        iftype = tun_type.lower()
        ifname = self.cli_detail("/interface %s print detail without-paging" % iftype, cached=True)
        for n1, f1, r1 in ifname:
            if self.si["name"] == r1["name"]:
                #in eoip-tunnel on routerboard: 411AH firmware: 2.20, local-address is not exist
                if "local-address" in r1.keys():
                    tun["local_address"] = r1["local-address"]
                tun["remote_address"] = r1["remote-address"]
                return

    def get_mtu(self, r):
        if is_int(r.get("mtu")):
            return int(r["mtu"])
        if is_int(r.get("actual-mtu")):
            return int(r["actual-mtu"])
        return None

    def execute(self):
        ifaces = {}
        misc = {}
        # Get ifIndex
        n_ifindex = {}  # number -> ifIndex
        for n, f, r in self.cli_detail(
                "/interface print oid without-paging"
        ):
            n_ifindex[n] = int(r["name"].rsplit(".", 1)[-1])
        time.sleep(1)
        # Fill interfaces
        a = self.cli_detail(
            "/interface print detail without-paging")
        for n, f, r in a:
            if r["type"] in self.ignored_types:
                continue
            if not r["type"] in "vlan":  # TODO: Check other types
                ifaces[r["name"]] = {
                    "name": r["name"],
                    "type": self.type_map[r["type"]],
                    "admin_status": "X" not in f,
                    "oper_status": "R" in f,
                    "enabled_protocols": [],
                    "subinterfaces": []
                }
                misc[r["name"]] = {
                    "type": r["type"]
                }
                if n in n_ifindex:
                    ifaces[r["name"]]["snmp_ifindex"] = n_ifindex[n]
                if r["type"].startswith("ipip-") \
                or r["type"].startswith("eoip-"):
                    self.si = {
                        "name": r["name"],
                        "admin_status": "X" not in f,
                        "oper_status": "R" in f,
                        "enabled_afi": ["IPv4"],
                        "enabled_protocols": []
                    }
                    if self.get_mtu(r) is not None:
                        self.si["mtu"] = self.get_mtu(r)
                    if r["type"].startswith("ipip-"):
                        self.get_tunnel("IPIP", "R", "IPv4", ifaces)
                    if r["type"].startswith("eoip-"):
                        self.get_tunnel("EOIP", "R", "IPv4", ifaces)
                    if r["type"].startswith("gre-"):
                        self.get_tunnel("GRE", "R", "IPv4", ifaces)
                    ifaces[r["name"]]["subinterfaces"] += [self.si]
        time.sleep(1)
        # Refine ethernet parameters
        for n, f, r in self.cli_detail(
            "/interface ethernet print detail without-paging"):
            iface = ifaces[r["name"]]
            ifaces[r["name"]]["mac"] = r["mac-address"]
        # Attach `vlan` subinterfaces to parent
        for n, f, r in self.cli_detail(
            "/interface vlan print detail without-paging"):
            if r["interface"] in ifaces:
                i = ifaces[r["interface"]]
                self.si = {
                    "name": r["name"],
                    "mac": r.get("mac-address") or r.get("mac"),
                    "admin_status": "X" not in f,
                    "oper_status": "R" in f,
                    "enabled_afi": [],
                    "vlan_ids": [int(r["vlan-id"])],
                    "enabled_protocols": []
                }
                if self.get_mtu(r) is not None:
                    self.si["mtu"] = self.get_mtu(r)
                i["subinterfaces"] += [self.si]
        # process internal `switch` ports and vlans
        vlan_tags = {}
        # "RB532", "x86", CCR1009 not support internal switch port
        try:
            v = self.cli_detail(
                    "/interface ethernet switch port print detail without-paging")
            for n, f, r in v:
                if "vlan-mode" not in r:
                    continue
                if (r["vlan-mode"] in ["check", "secure"]) \
                and (r["vlan-header"] in ["add-if-missing", "leave-as-is"]):
                    vlan_tags[r["name"]] = True
                else:
                    vlan_tags[r["name"]] = False
        except self.CLISyntaxError:
            pass
        # "RB532", "x86", CCR1009 not support internal switch port
        try:
            # Attach subinterfaces with `BRIDGE` AFI to parent
            v = self.cli_detail(
                    "/interface ethernet switch vlan print detail without-paging")
            for n, f, r in v: 
                vlan_id = int(r["vlan-id"])
                ports = r["ports"].split(",")
                if not ports:
                    continue
                for p in ports:
                    if p not in ifaces:
                        continue
                    i = ifaces[p]
                    self.si = {
                        "name": p,
                        "mac": i.get("mac"),
                        "admin_status": i.get("admin_status"),
                        "oper_status": i.get("oper_status"),
                        "enabled_afi": ["BRIDGE"],
                        "enabled_protocols": [],
                        "tagged_vlans": []
                    }
                    if self.get_mtu(i) is not None:
                        self.si["mtu"] = self.get_mtu(i)
                    if p in vlan_tags:
                        if vlan_tags[p]:
                            self.si["tagged_vlans"] += [vlan_id]
                        else:
                            self.si["utagged_vlan"] = vlan_id
                    # Try to find in already created subinterfaces
                    found = False
                    for sub in i["subinterfaces"]:
                        if sub["name"] == p:
                            if p in vlan_tags:
                                if vlan_tags[p]:
                                    sub["tagged_vlans"] += [vlan_id]
                                else:
                                    sub["utagged_vlan"] = vlan_id
                                found = True
                    if not found:
                        i["subinterfaces"] += [self.si]
        except self.CLISyntaxError:
            pass
        # Refine ip addresses
        for n, f, r in self.cli_detail(
            "/ip address print detail without-paging"):
            if "X" in f:
                continue
            self.si = {}
            if r["interface"] in ifaces:
                i = ifaces[r["interface"]]
                t = misc[r["interface"]]
                if not i["subinterfaces"]:
                    self.si = {
                        "name": r["interface"],
                        "enabled_afi": [],
                        # XXX Workaround
                        "admin_status": i["admin_status"],
                        "oper_status": i["oper_status"],
                        "enabled_protocols": []
                    }
                    i["subinterfaces"] += [self.si]
                else:
                    self.logger.debug('\nError: subinterfaces already exists in ' \
                        'interface \n%s\n' % i)
                    continue
            else:
                for i in ifaces:
                    iface = ifaces[i]
                    for s in iface["subinterfaces"]:
                        if s["name"] == r["interface"]:
                            self.si = s
                            break
                    if self.si:
                        t = misc[i]
                        break
            if not self.si:
                self.logger.debug('Error: Interface name not found!!!')
                continue

            afi = "IPv6" if ":" in r["address"] else "IPv4"
            if afi not in self.si["enabled_afi"]:
                self.si["enabled_afi"] += [afi]
            if afi == "IPv4":
                a = self.si.get("ipv4_addresses", [])
                a += [r["address"]]
                self.si["ipv4_addresses"] = a
            else:
                a = self.si.get("ipv6_addresses", [])
                a += [r["address"]]
                self.si["ipv6_addresses"] = a
            # Tunnel types
            # XXX /ip address print detail do not print tunnels !!!
            # Need reworks !!!
            if t["type"].startswith("ppp-"):
                self.get_tunnel("PPP", f, afi, r)
            if t["type"].startswith("pppoe-"):
                self.get_tunnel("PPPOE", f, afi, r)
            if t["type"].startswith("ovpn-"):
                self.si["tunnel"] = {}
            if t["type"].startswith("l2tp-"):
                self.get_tunnel("L2TP", f, afi, r)
            if t["type"].startswith("pptp-"):
                self.get_tunnel("PPTP", f, afi, r)
            if t["type"].startswith("ovpn-"):
                self.get_tunnel("PPP", f, afi, r)
            if t["type"].startswith("sstp-"):
                self.get_tunnel("SSTP", f, afi, r)
        # bridge
        for n, f, r in self.cli_detail("/interface bridge print detail"):
            self.si = {}
            if r["name"] in ifaces:
                i = ifaces[r["name"]]
                if not i["subinterfaces"]:
                    self.si = {
                        "name": r["name"],
                        "enabled_afi": ["BRIDGE"],
                        # XXX Workaround
                        "admin_status": i["admin_status"],
                        "oper_status": i["oper_status"],
                        "mac": r["mac-address"],
                        "enabled_protocols": []
                    }
                    if self.get_mtu(i) is not None:
                        self.si["mtu"] = self.get_mtu(i)
                    i["subinterfaces"] += [self.si]
                else:
                    i["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
                if r["protocol-mode"] in ["stp", "rstp"]:
                    i["enabled_protocols"] += ["STP"]
        # bonding
        for n, f, r in self.cli_detail("/interface bonding print detail"):
            self.si = {}
            if r["name"] in ifaces:
                i = ifaces[r["name"]]
                if not i["subinterfaces"]:
                    self.si = {
                        "name": r["name"],
                        "enabled_afi": [],
                        # XXX Workaround
                        "admin_status": i["admin_status"],
                        "oper_status": i["oper_status"],
                        "mac": r["mac-address"],
                        "enabled_protocols": []
                    }
                    if self.get_mtu(i) is not None:
                        self.si["mtu"] = self.get_mtu(i)
                    i["subinterfaces"] += [self.si]
                if r["mode"] in ["802.3ad"]:
                    i["enabled_protocols"] += ["LACP"]
                if r["slaves"]:
                    slaves = r["slaves"].split(",")
                    for s in slaves:
                        if s in ifaces:
                            ifaces[s]["aggregated_interface"] = r["name"]
        # OSPF
        try:
            ospf_result = self.cli_detail("/routing ospf interface print detail")
            for n, f, r in ospf_result:
                self.si = {}
                if r["interface"] in ifaces:
                    i = ifaces[r["interface"]]
                    if not i["subinterfaces"]:
                        self.si = {
                            "name": r["interface"],
                            "enabled_afi": [],
                            # XXX Workaround
                            "admin_status": i["admin_status"],
                            "oper_status": i["oper_status"],
                            "enabled_protocols": ["OSPF"]
                        }
                        i["subinterfaces"] += [self.si]
                    else:
                        i["subinterfaces"][0]["enabled_protocols"] += ["OSPF"]
        except self.CLISyntaxError:
            pass
        # PIMm IGMP
        try:
            cli_result = self.cli_detail("/routing pim interface print detail")
            for n, f, r in cli_result:
                self.si = {}
                proto = r["protocols"].upper().split(",")
                if r["interface"] in ifaces:
                    i = ifaces[r["interface"]]
                    if not i["subinterfaces"]:
                        self.si = {
                            "name": r["interface"],
                            "enabled_afi": [],
                            # XXX Workaround
                            "admin_status": i["admin_status"],
                            "oper_status": i["oper_status"],
                            "enabled_protocols": [proto]
                        }
                        i["subinterfaces"] += [self.si]
                    else:
                        i["subinterfaces"][0]["enabled_protocols"] += [proto]
                for i in ifaces:
                    for si in ifaces[i].get("subinterfaces", []):
                        if si["name"] == r["interface"]:
                            for p in proto:
                                if not p in si["enabled_protocols"]:
                                    si["enabled_protocols"] += [p]
        except self.CLISyntaxError:
            pass

        return [{"interfaces": ifaces.values()}]
