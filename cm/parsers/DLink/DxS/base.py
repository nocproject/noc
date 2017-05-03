# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic DLink parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## Third-party modules
from pyparsing import nums, Word, Group, Optional, Suppress, Combine,\
    Literal, delimitedList
## NOC modules
from noc.cm.parsers.base import BaseParser
from noc.core.ip import IPv4
from noc.lib.validators import is_ipv4, is_int


class BaseDLinkParser(BaseParser):
    STATUSES = set(["sntp"])
    SERVICES = set(["telnet", "web", "ssh", "password_recovery"])

    def parse(self, config):
        # Various protocol statuses
        self.statuses = defaultdict(lambda: False)
        self.vlan_ids = {}  # name -> id
        for l in config.splitlines():
            if not l or l.startswith("#"):
                continue
            ll = l.split()
            if l.startswith("config ports "):
                self.parse_config_ports(ll)
            elif l.startswith("create vlan "):
                self.parse_create_vlan(ll)
            elif l.startswith("config vlan vlanid "):
                self.parse_config_vlan_vlanid(ll)
            elif l.startswith("config vlan "):
                self.parse_config_vlan(ll)
            elif l.startswith("create account "):
                self.parse_create_account(ll)
            elif l.startswith("config sntp "):
                self.parse_config_sntp(ll)
            elif l.startswith("disable password encryption"):
                self.get_service_fact("password_encryption").enabled = False
            elif l.startswith("enable password encryption"):
                self.get_service_fact("password_encryption").enabled = True
            elif l.startswith("create syslog host "):
                self.parse_syslog_host(ll)
            elif l.startswith("create iproute "):
                self.parse_iproute(ll)
            elif l.startswith("config snmp "):
                self.parse_config_snmp(ll)
            elif l.startswith("config port_security ports "):
                self.parse_port_security(ll)
            elif l.startswith("config traffic control "):
                self.parse_traffic_control(ll)
            elif len(ll) > 1 and ll[0] in ("enable", "disable"):
                if ll[1] in self.STATUSES:
                    self.statuses[ll[1]] = ll[0] == "enable"
                elif ll[1] in self.SERVICES:
                    s = self.get_service_fact(ll[1])
                    s.enabled = ll[0] == "enable"
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
            1:2,1:(5,6-9,15)
            1:2,1:(5,7,9),2:10
        """
        for s, _, _ in PORT_EXPR.scanString(expr):
            for x in s.asList():
                if isinstance(x, basestring):
                    # Single port
                    yield x
                elif len(x) == 2:
                    # Range
                    l, r = x
                    if ":" in l:
                        # 2:5-2:7
                        pfx = "%s:%%d" % l.split(":")[0]
                        for i in range(int(l.split(":")[1]), int(r.split(":")[-1]) + 1):
                            yield pfx % i
                    else:
                        # 5-7
                        for i in range(int(l), int(r) + 1):
                            yield str(i)
                elif x[1] == ":(":
                    pfx = "%s:%%s" % x[0]
                    for y in x[2:]:
                        if isinstance(y, basestring):
                            yield pfx % y
                        else:
                            for i in range(int(y[0]), int(y[1]) + 1):
                                yield pfx % i

    def next_item(self, tokens, name):
        """
        Search for keyword and return next item
        """
        if name in tokens:
            idx = tokens.index(name) + 1
            if idx < len(tokens):
                return tokens[idx]
            else:
                return None
        else:
            return None

    def get_items(self, tokens, *args):
        """
        Fetch and return list of items
        """
        return [self.next_item(tokens, p) for p in args]

    def next_bool_item(self, tokens, name):
        return self.next_item(tokens, name) == "enable"

    def get_bool_items(self, tokens, *args):
        return [self.next_bool_item(tokens, p) for p in args]

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

    def get_vlan_fact(self, id):
        return super(BaseDLinkParser, self).get_vlan_fact(
            self.vlan_ids.get(id, id)
        )

    def parse_create_vlan(self, tokens):
        """
        create vlan 306 tag 306
        create vlan tag tag 306
        """
        tag = self.next_item(tokens, "tag")
        if tag and is_int(tag):
            name = self.next_item(tokens, "vlan")
            vid = int(tag)
            self.get_vlan_fact(vid).name = name
            self.vlan_ids[tag] = vid
            self.vlan_ids[name] = vid
        else:
            if len(tokens) == 5 and tokens[3] == "tag" and is_int(tokens[4]):
                name = self.next_item(tokens, "vlan")
                vid = int(tokens[4])
                self.get_vlan_fact(vid).name = name
                self.vlan_ids[tag] = vid
                self.vlan_ids[name] = vid

    def parse_config_vlan_vlanid(self, tokens):
        """
        config vlan vlanid 601-603,605 add tagged 2,12,28
        """
        tagged = self.next_item(tokens, "tagged")
        if tagged:
            tv = [self.get_subinterface_fact(p) for p in self.iter_ports(tagged)]
        else:
            tv = []
        untagged = self.next_item(tokens, "untagged")
        if untagged:
            uv = [self.get_subinterface_fact(p) for p in self.iter_ports(untagged)]
        else:
            uv = []
        for vid in self.iter_ports(tokens[3]):
            for f in tv:
                f.tagged_vlans += [vid]
                f.add_afi("BRIDGE")
            for f in uv:
                f.untagged_vlan = vid
                f.add_afi("BRIDGE")

    def parse_config_vlan(self, tokens):
        """
        config vlan 307 add tagged 1:1,1:5,2:21-2:22 advertisement disable
        config vlan vlan307 add tagged 1:1,1:5,2:21-2:22 advertisement disable
        """
        if tokens[2] == "default":
            return
        vid = int(self.vlan_ids.get(tokens[2], tokens[2]))
        tagged = self.next_item(tokens, "tagged")
        if tagged:
            for i in self.iter_ports(tagged):
                si = self.get_subinterface_fact(i)
                si.tagged_vlans += [vid]
                si.add_afi("BRIDGE")
        untagged = self.next_item(tokens, "untagged")
        if untagged:
            for i in self.iter_ports(untagged):
                si = self.get_subinterface_fact(i)
                si.untagged_vlan = vid
                si.add_afi("BRIDGE")

    def parse_create_account(self, tokens):
        """
        create account <group> <name>
        """
        group = tokens[2]
        user = tokens[3]
        u = self.get_user_fact(user)
        u.groups = [group]

    def parse_config_sntp(self, tokens):
        """
        enable sntp
        config sntp primary IP1 secondary IP2 poll-interval 720
        """
        if not self.statuses["sntp"]:
            return
        primary = self.next_item(tokens, "primary")
        if primary:
            self.get_ntpserver_fact(primary)
        secondary = self.next_item(tokens, "secondary")
        if secondary:
            self.get_ntpserver_fact(secondary)

    def parse_config_snmp(self, tokens):
        """
        config snmp system_name <name>
        config snmp system_location <name>
        """
        if tokens[2] == "system_name":
            self.get_system_fact().hostname = tokens[3]
        elif tokens[2] == "system_location":
            self.get_system_fact().location = " ".join(tokens[3:])

    def parse_syslog_host(self, tokens):
        """
        create syslog host 1 severity informational facility local7 udp_port 514 ipaddress 10.101.10.1 state enable
        """
        if self.next_item(tokens, "state") != "enable":
            return
        address = self.next_item(tokens, "ipaddress")
        if address:
            self.get_sysloghost_fact(address)

    def parse_iproute(self, tokens):
        """
        create iproute default 10.254.10.129 1
        create iproute 10.0.0.0/255.252.0.0 null0
        create iproute 10.125.0.0/255.255.255.0 10.125.0.1 1 primary
        """
        if tokens[2] == "default":
            prefix = "0.0.0.0/0"
        else:
            net, mask = tokens[2].split("/")
            prefix = str(IPv4(net, netmask=mask))
        f = self.get_static_route_fact(prefix)
        if is_ipv4(tokens[3]):
            f.next_hop = tokens[3]
        else:
            f.interface = tokens[3]

    def parse_port_security(self, tokens):
        """
        config port_security ports 1:1-1:25 admin_state disable max_learning_addr 1 lock_address_mode DeleteOnReset
        """
        ports = self.next_item(tokens, "ports") or ""
        ps_max = self.next_item(tokens, "max_learning_addr")
        for p in self.iter_ports(ports):
            si = self.get_subinterface_fact(p)
            si.port_security = True
            if ps_max is not None:
                si.port_security_max = ps_max

    def parse_traffic_control(self, tokens):
        """
        config traffic control 1 broadcast enable multicast enable unicast enable action drop threshold 64 countdown 0 time_interval 5 
        config traffic control 49 broadcast disable multicast disable unicast disable action drop threshold 131072 countdown 0 time_interval 5 
        """
        ports = self.next_item(tokens, "control") or ""
        unicast = self.next_item(tokens, "unicast")
        multicast = self.next_item(tokens, "multicast")
        broadcast = self.next_item(tokens, "broadcast")
        for p in self.iter_ports(ports):
            si = self.get_subinterface_fact(p)
            if broadcast == "enable":
                si.traffic_control_broadcast = True
            if multicast == "enable":
                si.traffic_control_multicast = True
            if unicast == "enable":
                si.traffic_control_unicast = True


# Port expression parser
DIGITS = Word(nums)
PORT = Combine(DIGITS + Optional(Literal(":") + DIGITS))
# 1:(2,3,10-20)
PORT_RANGE_PT = Group(
    DIGITS + Literal(":(") +
    delimitedList(Group(DIGITS + Suppress(Literal("-")) + DIGITS) | DIGITS, delim=",") +
    Suppress(Literal(")"))
)
# 1:2-1:5
PORT_RANGE = Group(PORT + Suppress(Literal("-")) + PORT)
# Port expression
PORT_EXPR = delimitedList(PORT_RANGE_PT | PORT_RANGE | PORT, delim=",")
