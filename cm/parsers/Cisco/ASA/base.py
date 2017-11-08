# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Basic IOS parser
# ---------------------------------------------------------------------
# Copyright (C) 2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.cm.parsers.pyparser import BasePyParser
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST, DIGITS, ALPHANUMS
# NOC modules
from noc.core.ip import IPv4
from noc.lib.text import ranges_to_list
from noc.lib.validators import is_ipv4, is_int
# Third-party modules
from pyparsing import *


class BaseASAParser(BasePyParser):
    RX_INTERFACE_BLOCK = re.compile(
        r"^interface\s+(?P<name>\S+(?:\s+\d+\S*)?)\n"
        r"(?:\s+[^\n]*\n)*",
        re.MULTILINE
    )

    def __init__(self, managed_object):
        super(BaseASAParser, self).__init__(managed_object)

    def create_parser(self):
        # System
        HOSTNAME = LineStart() + Literal("hostname") + REST.copy().setParseAction(self.on_hostname)
        DOMAIN_NAME = LineStart() + Literal("domain-name") + REST.copy().setParseAction(self.on_domain_name)
        TIMEZONE = LineStart() + Literal("clock timezone") + REST.copy().setParseAction(self.on_timezone)
        # NAMESERVER = LineStart() + Literal("ip name-server") + REST.copy().setParseAction(self.on_nameserver)
        USER = LineStart() + Literal("username") + (
        Word(alphanums + "-_") + Optional(Literal("privilege") + DIGITS)).setParseAction(self.on_user) + REST
        SERVICE = LineStart() + (
        Optional(Literal("no")) + Literal("service") + Word(alphanums) + restOfLine).setParseAction(self.on_service)
        SSH_VERSION = LineStart() + Literal("ssh version") + (Word(nums) + restOfLine).setParseAction(
            self.on_ssh_version)
        HTTP_SERVER = LineStart() + Optional(Literal("no")) + Literal("http server") + (
        Literal("enable") + Optional(DIGITS).copy() + restOfLine).setParseAction(self.on_http_server)

        SYSTEM_BLOCK = (
            HOSTNAME |
            DOMAIN_NAME |
            TIMEZONE |
            #    NAMESERVER |
            USER |
            SERVICE |
            SSH_VERSION |
            HTTP_SERVER
        )
        # VLAN
        # VLAN_RANGE = LineStart() + Literal("vlan") + Combine(DIGITS + Word("-,") + restOfLine).setParseAction(self.on_vlan_range)
        # VLAN = LineStart() + Literal("vlan") + DIGITS.copy().setParseAction(self.on_vlan)
        # VLAN_NAME = Literal("name") + REST.copy().setParseAction(self.on_vlan_name)
        # VLAN_BLOCK = VLAN + ZeroOrMore(INDENT + (VLAN_NAME | LINE))
        # Interface
        INTERFACE = LineStart() + Literal("interface") + REST.copy().setParseAction(self.on_interface)
        INTERFACE_ENCVLAN = (Optional(Literal("no")) + Literal("vlan") + Optional(DIGITS).copy()).setParseAction(
            self.on_interface_encvlan)
        INTERFACE_NAMEIF = Literal("nameif") + REST.copy().setParseAction(self.on_interface_nameif)
        INTERFACE_ADDRESS = Literal("ip address") + (IPv4_ADDRESS("address") + IPv4_ADDRESS("mask")).setParseAction(
            self.on_interface_address)
        INTERFACE_ADDRESS_SECONDARY = Literal("ip address") + (
        IPv4_ADDRESS("address") + IPv4_ADDRESS("mask") + Literal("secondary")).setParseAction(self.on_interface_address)
        INTERFACE_SHUTDOWN = (Optional(Literal("no")) + Literal("shutdown")).setParseAction(self.on_interface_shutdown)
        INTERFACE_SPEED = Literal("speed") + ALPHANUMS.copy().setParseAction(self.on_interface_speed)
        INTERFACE_DUPLEX = Literal("duplex") + ALPHANUMS.copy().setParseAction(self.on_interface_duplex)
        INTERFACE_UNTAGGED = Literal("switchport") + Literal("access") + Literal("vlan") + DIGITS.copy().setParseAction(
            self.on_interface_untagged)
        INTERFACE_TAGGED = (
            Literal("switchport") + Literal("trunk") +
            Literal("allowed") + Literal("vlan") +
            REST.copy().setParseAction(self.on_interface_tagged)
        )
        # INTERFACE_ACL = Literal("ip access-group") + (Word(alphanums + "-_") + (Literal("in") | Literal("out"))).setParseAction(self.on_interface_acl)
        INTERFACE_BLOCK = INTERFACE + ZeroOrMore(INDENT + (
            INTERFACE_ENCVLAN |
            INTERFACE_NAMEIF |
            INTERFACE_ADDRESS_SECONDARY |
            INTERFACE_ADDRESS |
            INTERFACE_SHUTDOWN |
            #    INTERFACE_REDIRECTS |
            #    INTERFACE_PROXY_ARP |
            INTERFACE_SPEED |
            INTERFACE_DUPLEX |
            INTERFACE_UNTAGGED |
            INTERFACE_TAGGED |
            #    INTERFACE_CDP |
            #    INTERFACE_ISIS |
            #    INTERFACE_ISIS_METRIC |
            #    INTERFACE_ISIS_PTP |
            #    INTERFACE_MPLS_IP |
            #    INTERFACE_ACL |
            LINE
        ))

        # Logging
        LOGGING_HOST = LineStart() + Literal("logging host") + Word(alphanums) + IPv4_ADDRESS.copy().setParseAction(
            self.on_logging_host)
        LOGGING_BLOCK = LOGGING_HOST
        # NTP
        NTP_SERVER = LineStart() + Literal("ntp") + Literal("server") + IPv4_ADDRESS.copy().setParseAction(
            self.on_ntp_server)
        NTP_BLOCK = NTP_SERVER
        # VRF
        # Static Route
        # STATIC_ROUTE = LineStart() + Literal("route") + Word(alphanums) + (IPv4_ADDRESS("net") + IPv4_ADDRESS("mask") + REST).setParseAction(self.on_ipv4_route)

        CONFIG = (
            INTERFACE_BLOCK |
            SYSTEM_BLOCK |
            #    VLAN_RANGE |
            #    VLAN_BLOCK |
            LOGGING_BLOCK |
            NTP_BLOCK |
            #    VRF_BLOCK |
            #    STATIC_ROUTE |
            LINE
        )
        return CONFIG

    def get_interface_defaults(self, name):
        r = {
            "admin_status": True,
            "protocols": []
        }
        # @todo: Replace with more reliable type detection
        return r

    def get_subinterface_defaults(self):
        return {
            "admin_status": True
        }

    def get_user_defaults(self):
        return {
            "level": 0
        }

    def on_hostname(self, tokens):
        self.get_system_fact().hostname = tokens[0]

    def on_domain_name(self, tokens):
        self.get_system_fact().domain_name = tokens[0]

    def on_timezone(self, tokens):
        self.get_system_fact().timezone = tokens[0]

    # def on_nameserver(self, tokens):
    #    self.get_system_fact().nameservers += [tokens[0]]

    def on_user(self, tokens):
        tokens = list(tokens)
        user = self.get_user_fact(tokens[0])
        if "privilege" in tokens:
            i = tokens.index("privilege")
            user.level = int(tokens[i + 1])

    def on_service(self, tokens):
        """
        [no] service <name> <config>
        """
        enabled = tokens[0] != "no"
        if not enabled:
            tokens = tokens[1:]
        name = tokens[1]
        sf = self.get_service_fact(name)
        sf.enabled = enabled

    def on_ssh_version(self, tokens):
        sf = self.get_service_fact("ssh")
        sf.enabled = True
        sf.version = tokens[0]

    def on_interface(self, tokens):
        name = tokens[0]
        if "." in name:
            i_name = name.split(".")[0]
        else:
            i_name = name
        self.get_subinterface_fact(name, i_name)

    def on_interface_encvlan(self, tokens):
        status = tokens[0] == "no"
        si = self.get_current_subinterface()
        if status:
            si.vlan_ids = None
        else:
            encvlan = tokens[1]
            if encvlan.startswith("\"") and encvlan.startswith("\""):
                encvlan = encvlan[1:-1]
            si.vlan_ids = [encvlan]
        si.add_afi("BRIDGE")
        # if "." not in si.name:
        #    si.interface.vlan_ids += [encvlan]

    def on_interface_nameif(self, tokens):
        si = self.get_current_subinterface()
        nameif = tokens[0]
        if nameif.startswith("\"") and nameif.startswith("\""):
            nameif = nameif[1:-1]
        si.description = nameif
        if "." not in si.name:
            si.interface.description = nameif

    def on_interface_address(self, tokens):
        ip = str(IPv4(tokens[0], netmask=tokens[1]))
        si = self.get_current_subinterface()
        if len(tokens) > 2 and tokens[2] == "secondary":
            si.ipv4_addresses += [ip]
        else:
            si.ipv4_addresses = [ip] + si.ipv4_addresses
        si.add_afi("IPv4")

    def on_interface_shutdown(self, tokens):
        status = tokens[0] == "no"
        si = self.get_current_subinterface()
        si.admin_status = status
        if "." not in si.name:
            si.interface.admin_status = status

    def on_interface_speed(self, tokens):
        self.get_current_interface().speed = tokens[-1]

    def on_interface_duplex(self, tokens):
        self.get_current_interface().duplex = tokens[-1]

    def on_interface_untagged(self, tokens):
        si = self.get_current_subinterface()
        si.untagged_vlan = int(tokens[0])
        si.add_afi("BRIDGE")

    def on_interface_tagged(self, tokens):
        vlans = tokens[0].strip()
        if vlans.startswith("add"):
            vlans = vlans.split(" ", 1)[1].strip()
        si = self.get_current_subinterface()
        if vlans != "none":
            for v in ranges_to_list(vlans):
                si.tagged_vlans += [int(v)]
        si.add_afi("BRIDGE")

    def on_logging_host(self, tokens):
        self.get_sysloghost_fact(tokens[0])

    def on_ntp_server(self, tokens):
        self.get_ntpserver_fact(tokens[0])

    def on_vlan(self, tokens):
        self.get_vlan_fact(int(tokens[0].strip()))

    def on_vlan_range(self, tokens):
        for v in ranges_to_list(tokens[0].strip()):
            self.get_vlan_fact(v)

    def on_vlan_name(self, tokens):
        self.get_current_vlan().name = tokens[0]

    def on_http_server(self, tokens):
        self.get_service_fact("http").enabled = tokens[0] == "enable"
        if len(tokens) > 1:
            self.get_service_fact("http").port = tokens[1]

    def on_ipv4_route(self, tokens):
        p = IPv4(tokens[0], netmask=tokens[1])
        sf = self.get_static_route_fact(str(p))
        rest = tokens[2].split()
        nh = rest.pop(0)
        if is_ipv4(nh):
            sf.next_hop = nh
        else:
            iface = self.convert_interface_name(nh)
            if iface.startswith("Nu"):
                sf.discard = True
            else:
                sf.interface = iface
        if rest and is_int(rest[0]):
            sf.distance = rest.pop(0)
        while rest:
            if rest[0] == "name":
                sf.description = rest[1]
                rest = rest[2:]
            elif rest[0] == "tag":
                sf.tag = rest[1]
                rest = rest[2:]
            else:
                break
