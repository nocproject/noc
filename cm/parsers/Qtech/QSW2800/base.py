# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Basic Junos parser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# Third-party modules
from pyparsing import OneOrMore, Word, alphanums, QuotedString
# NOC modules
from noc.core.ip import IPv4
from noc.cm.parsers.base import BaseParser
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST, DIGITS, ALPHANUMS
from noc.lib.text import ranges_to_list


class BaseQSW2800Parser(BaseParser):

    def __init__(self, managed_object):
        super(BaseQSW2800Parser, self).__init__(managed_object)

    def parse(self, config):
        VALUE = OneOrMore(Word(alphanums + "-/.:_+[],") | QuotedString("\""))
        context = []
        inactive_level = 1
        for l in config.splitlines():
            no = False
            l = l.rstrip()
            if "no " in l:
                l = l.replace("no ", "")
                no = True
            # if l == "{master}":
            if not l:
                continue
            elif l.startswith(" "*inactive_level):
                inactive_level = len(context) + 1
                context += [l.split()[0].strip()]
            elif "set" in l:
                inactive_level = len(context) + 1
            elif "exit" in l:
                context.pop(-1)
                inactive_level = len(context) - 1
            elif "!" in l and context:
                context = []
                inactive_level = inactive_level - 1
                # continue
                # if inactive_level is not None and inactive_level >= len(context):
                #    inactive_level = None
            elif "!" in l:
                print("Skipping line")
                continue
            elif context and len(context) >= inactive_level:
                if context[-1] not in l:
                    context.pop(-1)
                    context += [l.split()[0].strip()]
            else:
                context += [l.split()[0].strip()]
            cp = " ".join(context).split() + l.split()
            h = self.handlers
            # print cp
            for p in cp:
                if p in h:
                    h = h[p]
                elif "*" in h:
                    h = h["*"]
                else:
                    break
                if callable(h):
                    h(self, VALUE.parseString(" ".join(cp)))
                    break
                elif h is None:
                    break
        # Yield facts
        for f in self.iter_facts():
            yield f

    def get_interface_defaults(self, name):
        r = super(BaseQSW2800Parser, self).get_interface_defaults(name)
        r["admin_status"] = True
        return r

    def get_subinterface_defaults(self):
        r = super(BaseQSW2800Parser, self).get_subinterface_defaults()
        r["admin_status"] = True
        return r

    def on_interface_context(self, tokens):
        iface = self.get_interface_fact(tokens[2])
        si = self.get_subinterface_fact(tokens[2])

    def on_sub_interface_context(self, tokens):
        si = self.get_subinterface_fact(tokens[2])

    def on_system_host_name(self, tokens):
        self.get_system_fact().hostname = tokens[-1]

    def on_snmp_contact(self, tokens):
        pass

    def on_snmp_location(self, tokens):
        self.get_system_fact().location = " ".join(tokens[2:])
        print tokens

    def on_system_time_zone(self, tokens):
        self.get_system_fact().timezone = tokens[3]

    def on_system_login_user_class(self, tokens):
        self.get_user_fact(tokens[2]).level = tokens[4]

    def on_interface_description(self, tokens):
        iface = self.get_current_interface()
        iface.description = tokens[-1]

    def on_interface_switchport(self, tokens):
        si = self.get_current_subinterface()
        if len(tokens) == 3:
            cmd = [tokens[3], None]
        elif len(tokens) >= 4:
            cmd = tokens[3:5]
        else:
            cmd = None
        if ["access", "vlan"] == cmd:
            si.vlan_ids = [tokens[-1]]
        if ["port-security"] == cmd:
            si.port_security = True
        if ["port-security", "maximum"] == cmd:
            si.port_security_max = tokens[-1]

    def on_interface_igmp(self, tokens):
        pass

    def on_subinterface_ipv4_address(self, tokens):
        """
        set interface <N> unit <M> family inet address <K>
        """
        si = self.get_current_subinterface()
        cmd = tokens[3] if len(tokens) >= 3 else None
        if "address" == cmd:
            si.ipv4_addresses += [tokens[-2]]
            si.add_afi("IPv4")

    def on_subinterface_description(self, tokens):
        """
        set interface <N> unit <M> description "<K>"
        """
        self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3])).description = tokens[-1]

    def on_storm_control(self, tokens):
        si = self.get_current_subinterface()
        cmd = tokens[3] if len(tokens) >= 3 else None
        # if "broadcast" in tokens or tokens[3]=="broadcast":
        if cmd == "broadcast":
            si.traffic_control_broadcast = True
        if cmd == "multicast":
            si.traffic_control_multicast = True
        if cmd == "unicast":
            si.traffic_control_unicast = True

    def on_system_logging_host(self, tokens):
        self.get_sysloghost_fact(tokens[-3])

    def on_vlan(self, tokens):
        """
         if - vlan range
         database - 
        :param tokens: 
        :return: 
        """
        if "-" not in tokens[-1] or "database" not in tokens:
            self.get_vlan_fact(int(tokens[-1].strip()))

    def on_vlan_name(self, tokens):
            self.get_current_vlan().name = tokens[-1]

    def on_system_ntp_server(self, tokens):
        """
        ntp server 1.2.5.9
        """
        if tokens[2] != "enable":
            self.get_ntpserver_fact(tokens[-1])

    def on_static_route(self, tokens):
        """
        ip default-gateway 1.2.5.9
        :param tokens: 
        """
        # print tokens
        if tokens[2] == "default-gateway":
            prefix = IPv4("0.0.0.0", netmask="0.0.0.0")
            self.get_static_route_fact(str(prefix)).next_hop = tokens[-1]

    def on_protocol(self, tokens):
        pass

    """
    def set_facts(self, fact=None):
        # print kwargs
        # k = {"fact": "system", "hostname": "host"}
        if "fact" in k:
            f = "self.get_%s_fact" % k["fact"]
            if callable(f):
                # f().__setattr__(kwargs.pop("fact"))
        #
        pass
    """

    handlers = {
        # ["interface", "*", "description", "*"] -> {fact: "interface", name: "$1", description: "$2"}
        "hostname": on_system_host_name,
        "sysLocation": on_snmp_location,
        "sysContact": on_snmp_contact,
        "logging": on_system_logging_host,
        "clock": on_system_time_zone,
        "username": on_system_login_user_class,
        "vlan": {
            "vlan": on_vlan,
            "*": {
                "name": on_vlan_name
            }
        },
        "ip": on_static_route,
        "snmp-server": {
        },
        "Interface": {
            "Interface": on_interface_context,
            "*": {
                "ip": on_subinterface_ipv4_address,
                "description": on_interface_description,
                "switchport": on_interface_switchport,
                "igmp": on_interface_igmp,
                "storm-control": on_storm_control,
                "lldp": on_protocol,
            }
        },
        "interface": {
            "interface": on_sub_interface_context,
            "*": {
                "ip": on_subinterface_ipv4_address,
            }
        },
        "ntp": on_system_ntp_server
    }
