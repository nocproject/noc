# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic DLink parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.parsers.base import BaseParser


class DLinkParser(BaseParser):
    def parse(self, config):
        for l in config.splitlines():
            if not l or l.startswith("#"):
                continue
            ll = l.split()
            if l.startswith("config ports "):
                self.parse_config_ports(ll)
            elif l.startswith("create vlan "):
                self.parse_create_vlan(ll)
            elif l.startswith("config vlan "):
                self.parse_config_vlan(ll)
            # Yield facts
            for f in self.iter_facts():
                yield f

    def iter_ports(self, expr):
        """
        Iterate via port expressions.
        Expr can be one of:
            1
            1,2,5
            1,2-4,7
            2:2,2:5-2:7,2:9
        """
        for p in expr.split(","):
            if "-" in p:
                l, r = p.split("-")
                if ":" in l and ":" in r:
                    pfx = l.split(":")[0] + ":%d"
                    for i in range(int(l.split(":")[1]), int(r.split(":")[1]) + 1):
                        yield pfx % i
                else:
                    for i in range(int(l), int(r) + 1):
                        yield str(i)
            else:
                yield p

    def next_item(self, tokens, name):
        """
        Search for keyword and return next item
        """
        if name in tokens:
            return tokens[tokens.index(name) + 1]
        else:
            return None

    def parse_config_ports(self, tokens):
        """
        config ports 1:7,1:9,1:11,1:13 speed auto
        capability_advertised 1000_full flow_control disable
        learning enable state enable description MYDESCRIPTION
        """
        speed = self.next_item(tokens, "speed")
        admin_status = self.next_item(tokens, "state") == "enable"
        desc = self.next_item(tokens, "description")
        for p in self.iter_ports(tokens[2]):
            iface = self.get_interface_fact(p)
            # speed
            if speed:
                iface.speed = speed
            # state
            iface.admin_status = admin_status
            # description
            if desc:
                iface.description = desc

    def parse_create_vlan(self, tokens):
        """
        create vlan 306 tag 306
        """
        tag = self.next_item(tokens, "tag")
        if tag:
            self.get_vlan_fact(int(tag)).name = tokens[2]

    def parse_config_vlan(self, tokens):
        """
        config vlan 307 add tagged 1:1,1:5,2:21-2:22 advertisement disable
        """
        if tokens[2] == "default":
            return
        vid = int(tokens[2])
        tagged = self.next_item(tokens, "tagged")
        if tagged:
            for i in self.iter_ports(tagged):
                self.get_subinterface_fact(i).tagged_vlans += [vid]
        untagged = self.next_item(tokens, "untagged")
        if untagged:
            for i in self.iter_ports(untagged):
                self.get_subinterface_fact(i).untagged_vlan = vid
