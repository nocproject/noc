# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_interfaces"
    implements = [IGetInterfaces]

    type_map = {
        "ether": "physical",
        "wlan": "physical",
        "bridge": "SVI",
        "vlan": "SVI",
        "pptp-out": "tunnel",
        "pptp-in": "tunnel",
        "gre-tunnel": "tunnel"
    }
    si = {}

    def get_tunnel(self, tun_type, f, afi, ipif):
        self.si["tunnel"] = {}
        tun = self.si["tunnel"]
        tun["type"] = tun_type
        if tun_type in ["PPP", "PPPOE", "L2TP", "PPTP"]:
            if (f == "D" and afi == "IPv4"):
                tun["local_address"] = ipif["address"].split("/", 1)[0].strip()
                tun["remote_address"] = ipif["network"]
                return
        iftype = tun_type.lower()
        for n1, f1, r1 in self.cli_detail(
            "/interface %s print detail without-paging" % iftype, cached=True):
            if self.si["name"] == r1["name"]:
                tun["local_address"] = r1["local-address"]
                tun["remote_address"] = r1["remote-address"]
                return

    def execute(self):
        ifaces = {}
        misc = {}
        # Fill interfaces
        for n, f, r in self.cli_detail(
            "/interface print detail without-paging"):
            if not r["type"] in "vlan":
                ifaces[r["name"]] = {
                    "name": r["name"],
                    "type": self.type_map[r["type"]],
                    "admin_status": "X" not in f,
                    "oper_status": "R" in f,
                    "subinterfaces": []
                }
                misc[r["name"]] = {
                    "type": r["type"]
                }
        # Refine ethernet parameters
        for n, f, r in self.cli_detail(
            "/interface ethernet print detail without-paging"):
            iface = ifaces[r["name"]]
            ifaces[r["name"]]["mac"] = r["mac-address"]
            # Attach `vlan` subinterfaces to physical parent
            for n1, f1, r1 in self.cli_detail(
                "/interface vlan print detail without-paging", cached=True):
                if r["name"] == r1["interface"]:
                    i = ifaces[r1["interface"]]
                    self.si = {
                        "name": r1["name"],
                        "mac": r1["mac-address"],
                        "mtu": r1["mtu"],
                        "admin_status": "X" not in f1,
                        "oper_status": "R" in f1,
                        "enabled_afi": [],
                        "tagged_vlans": [int(r1["vlan-id"])]
                    }
                    i["subinterfaces"] += [self.si]
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
                        "oper_status": i["oper_status"]
                    }
                    i["subinterfaces"] += [self.si]
                else:
                    self.debug('Error: subinterfaces already exists !!!')
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
                self.debug('Error: Interface name not found!!!')
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
            if t["type"].startswith("gre-"):
                self.get_tunnel("GRE", f, afi, r)
            if t["type"].startswith("ipip-"):
                self.get_tunnel("IPIP", f, afi, r)
        return [{"interfaces": ifaces.values()}]
