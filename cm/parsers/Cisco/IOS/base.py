# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic IOS parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from pyparsing import *
## NOC modules
from noc.lib.ip import IPv4
from noc.cm.parsers.pyparser import BasePyParser
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST


class BaseIOSParser(BasePyParser):
    def create_parser(self):
        # System
        HOSTNAME = LineStart() + Literal("hostname") + REST.copy().setParseAction(self.on_hostname)
        DOMAIN_NAME = LineStart() + Literal("ip") + Literal("domain-name") + REST.copy().setParseAction(self.on_domain_name)
        TIMEZONE = LineStart() + Literal("clock") + Literal("timezone") + REST.copy().setParseAction(self.on_timezone)
        NAMESERVER = LineStart() + Literal("ip") + Literal("name-server") + REST.copy().setParseAction(self.on_nameserver)
        SYSTEM_BLOCK = HOSTNAME | DOMAIN_NAME | TIMEZONE | NAMESERVER
        # Interface
        INTERFACE = LineStart() + Literal("interface") + REST.copy().setParseAction(self.on_interface)
        INTERFACE_DESCRIPTION = Literal("description") + REST.copy().setParseAction(self.on_interface_descripion)
        INTERFACE_ADDRESS = Literal("ip") + Literal("address") + (IPv4_ADDRESS("address") + IPv4_ADDRESS("mask")).setParseAction(self.on_interface_address)
        INTERFACE_SHUTDOWN = (Optional(Literal("no")) + Literal("shutdown")).setParseAction(self.on_interface_shutdown)
        INTERFACE_REDIRECTS = (Optional(Literal("no")) + Literal("ip") + Literal("redirects")).setParseAction(self.on_interface_redirects)
        INTERFACE_PROXY_ARP = (Optional(Literal("no")) + Literal("ip") + Literal("proxy-arp")).setParseAction(self.on_interface_proxy_arp)
        INTERFACE_BLOCK = INTERFACE + ZeroOrMore(INDENT + (
            INTERFACE_DESCRIPTION |
            INTERFACE_ADDRESS |
            INTERFACE_SHUTDOWN |
            INTERFACE_REDIRECTS |
            INTERFACE_PROXY_ARP |
            LINE
        ))
        # Logging
        LOGGING_HOST = LineStart() + Literal("logging") + IPv4_ADDRESS.copy().setParseAction(self.on_logging_host)
        LOGGING_BLOCK = LOGGING_HOST
        # NTP
        NTP_SERVER = LineStart() + Literal("ntp") + Literal("server") + IPv4_ADDRESS.copy().setParseAction(self.on_ntp_server)
        NTP_BLOCK = NTP_SERVER

        CONFIG = SYSTEM_BLOCK | INTERFACE_BLOCK | LOGGING_BLOCK | NTP_BLOCK
        return CONFIG

    def get_interface_defaults(self):
        return {
            "admin_status": False,
        }

    def get_subinterface_defaults(self):
        return {
            "ip_redirects": True,
            "ip_proxy_arp": True
        }

    def on_hostname(self, tokens):
        self.get_system_fact().hostname = tokens[0]

    def on_domain_name(self, tokens):
        self.get_system_fact().domain_name = tokens[0]

    def on_timezone(self, tokens):
        self.get_system_fact().timezone = tokens[0]

    def on_nameserver(self, tokens):
        self.get_system_fact().nameservers += [tokens[0]]

    def on_interface(self, tokens):
        name = tokens[0]
        if "." in name:
            i_name = name.split(".")[0]
        else:
            i_name = name
        self.get_subinterface_fact(name, i_name)

    def on_interface_descripion(self, tokens):
        si = self.get_current_subinterface()
        description = tokens[0]
        si.description = description
        if "." not in si.name:
            si.interface.description = description

    def on_interface_address(self, tokens):
        ip = str(IPv4(tokens[0], netmask=tokens[1]))
        self.get_current_subinterface().ipv4_addresses += [ip]

    def on_interface_shutdown(self, tokens):
        status = tokens[0] == "no"
        si = self.get_current_subinterface()
        si.admin_status = status
        if "." not in si.name:
            si.interface.admin_status = status

    def on_interface_redirects(self, tokens):
        self.get_current_subinterface().ip_redirects = tokens[0] != "no"

    def on_interface_proxy_arp(self, tokens):
        self.get_current_subinterface().ip_proxy_arp = tokens[0] != "no"

    def on_logging_host(self, tokens):
        self.get_sysloghost_fact(tokens[0])

    def on_ntp_server(self, tokens):
        self.get_ntpserver_fact(tokens[0])
