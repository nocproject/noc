# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic RouterOS parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from collections import defaultdict
## Third-party modules
from pyparsing import *
## NOC modules
from noc.lib.ip import IPv4
from noc.cm.parsers.pyparser import BasePyParser
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST, DIGITS, ALPHANUMS
from noc.lib.text import ranges_to_list


class RouterOSParser(BasePyParser):
    rx_continue = re.compile(r"\\\n\s*", re.MULTILINE)
    SPEED_MAP = {
        "1Gbps": 1000,
        "100Mbps": 100
    }

    def __init__(self, managed_object):
        super(RouterOSParser, self).__init__(managed_object)
        self.context = None
        self.add_handler = None
        self.set_handler = None
        self.slave_ports = defaultdict(list)

    def preprocess(self, config):
        return self.rx_continue.sub(" ", config)

    def create_parser(self):
        LBRACKET, RBRACKET, EQ, QUOTE, SLASH = map(Suppress, "[]=\"/")
        KEY = Word(alphanums + "-")
        VALUE = Word(alphanums + "-/.:_+") | QuotedString("\"")
        FIND = LBRACKET + Group(Literal("find") + Literal("default-name") + EQ + VALUE) + RBRACKET
        KVP = Group(KEY + EQ + VALUE)
        BEGIN = LineStart() + SLASH + restOfLine.setParseAction(self.on_begin)
        ADD_OP = LineStart() + Literal("add") + ZeroOrMore(KVP).setParseAction(self.on_add)
        SET_OP = LineStart() + Literal("set") + (Optional(FIND | KEY + ~FollowedBy(EQ) | QuotedString("\"")) + ZeroOrMore(KVP)).setParseAction(self.on_set)
        CONFIG = ZeroOrMore(BEGIN | ADD_OP | SET_OP)
        return CONFIG

    def on_begin(self, tokens):
        self.context = tokens[0]
        h = self.context.replace(" ", "_").replace("-", "_")
        self.add_handler = getattr(self, "on_%s_add" % h, None)
        self.set_handler = getattr(self, "on_%s_set" % h, None)

    def parse_kvp(self, tokens):
        return dict((k, v) for k, v in tokens)

    def get_interface_fact(self, name):
        if isinstance(name, basestring):
            return super(RouterOSParser, self).get_interface_fact(name)
        else:
            default_name = name[2]
            for i in self.interface_facts.itervalues():
                if getattr(i, "default_name") == default_name:
                    self.current_interface = i
                    return i
            i = super(RouterOSParser, self).get_interface_fact(default_name)
            i.default_name = default_name
            return i

    def get_interface_defaults(self, name):
        r = {
            "admin_status": True,
            "protocols": []
        }
        return r

    def on_set(self, tokens):
        if self.set_handler:
            if isinstance(tokens[0], basestring) or tokens[0][0] == "find":
                name = tokens[0]
                args = self.parse_kvp(tokens[1:])
            else:
                name = None
                args = self.parse_kvp(tokens)
            self.set_handler(name, args)

    def on_add(self, tokens):
        if self.add_handler:
            self.add_handler(self.parse_kvp(tokens))

    def on_system_identity_set(self, name, args):
        """
        /system identity
        set name=hostname
        """
        if "name" in args:
            self.get_system_fact().hostname = args["name"]

    def on_system_clock_manual_set(self, name, args):
        """
        /system clock manual
        set time-zone=+04:00
        """
        if "time-zone" in args:
            self.get_system_fact().timezone = args["time-zone"]

    def on_ip_service_set(self, name, args):
        """
        /ip service
        set telnet disabled=yes
        """
        self.get_service_fact(name).enabled = args.get("disabled") != "yes"

    def on_system_ntp_client_set(self, name, args):
        """
        /system ntp client
        set enabled=yes primary-ntp=1.1.1.1 secondary-ntp=2.2.2.2
        """
        if args.get("enabled") == "yes":
            if "primary-ntp" in args:
                self.get_ntpserver_fact(args["primary-ntp"])
            if "secondary-ntp" in args:
                self.get_ntpserver_fact(args["secondary-ntp"])

    def on_interface_ethernet_set(self, name, args):
        iface = self.get_interface_fact(name)
        if "name" in args:
            iface.name = args["name"]
        if "mac-address" in args:
            iface.mac = args["mac-address"]
        if "speed" in args:
            iface.speed = self.SPEED_MAP.get(args["speed"])
        if "master-port" in args:
            self.slave_ports[args["master-port"]] += [iface]
        if "comment" in args:
            iface.description = args["comment"]
        if "disabled" in args:
            iface.admin_status = args["disabled"] != "yes"

    def on_ip_route_add(self, args):
        if args.get("disabled", "no") != "no":
            return
        if "dst-address" not in args:
            return
        f = self.get_static_route_fact(args["dst-address"])
        if "gateway" in args:
            f.next_hop = args["gateway"]
        if "distance" in args:
            f.distance = args["distance"]
