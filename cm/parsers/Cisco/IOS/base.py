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
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST, DIGITS, ALPHANUMS
from noc.lib.text import ranges_to_list


class BaseIOSParser(BasePyParser):
    def __init__(self, managed_object):
        super(BaseIOSParser, self).__init__(managed_object)
        self.enable_cdp = True

    def create_parser(self):
        # System
        HOSTNAME = LineStart() + Literal("hostname") + REST.copy().setParseAction(self.on_hostname)
        DOMAIN_NAME = LineStart() + Literal("ip") + Literal("domain-name") + REST.copy().setParseAction(self.on_domain_name)
        TIMEZONE = LineStart() + Literal("clock") + Literal("timezone") + REST.copy().setParseAction(self.on_timezone)
        NAMESERVER = LineStart() + Literal("ip") + Literal("name-server") + REST.copy().setParseAction(self.on_nameserver)
        USER = LineStart() + Literal("username") + (Word(alphanums + "-_") + Optional(Literal("privilege") + DIGITS)).setParseAction(self.on_user) + REST
        CDP_RUN = LineStart() + (Optional(Literal("no")) + Literal("cdp") + Literal("run")).setParseAction(self.on_cdp_run)
        SERVICE = LineStart() + (Optional(Literal("no")) + Literal("service") + Word(alphanums + "-") + restOfLine).setParseAction(self.on_service)
        SSH_VERSION = LineStart() + Literal("ip") + Literal("ssh") + Literal("version") + (Word(nums) + restOfLine).setParseAction(self.on_ssh_version)
        SYSTEM_BLOCK = (
            HOSTNAME |
            DOMAIN_NAME |
            TIMEZONE |
            NAMESERVER |
            USER |
            CDP_RUN |
            SERVICE |
            SSH_VERSION
        )
        # VLAN
        VLAN_RANGE = LineStart() + Literal("vlan") + Combine(DIGITS + Word("-,") + restOfLine).setParseAction(self.on_vlan_range)
        VLAN = LineStart() + Literal("vlan") + DIGITS.copy().setParseAction(self.on_vlan)
        VLAN_NAME = Literal("name") + REST.copy().setParseAction(self.on_vlan_name)
        VLAN_BLOCK = VLAN + ZeroOrMore(INDENT + (VLAN_NAME | LINE))
        # Interface
        INTERFACE = LineStart() + Literal("interface") + REST.copy().setParseAction(self.on_interface)
        INTERFACE_DESCRIPTION = Literal("description") + REST.copy().setParseAction(self.on_interface_descripion)
        INTERFACE_ADDRESS = Literal("ip") + Literal("address") + (IPv4_ADDRESS("address") + IPv4_ADDRESS("mask")).setParseAction(self.on_interface_address)
        INTERFACE_SHUTDOWN = (Optional(Literal("no")) + Literal("shutdown")).setParseAction(self.on_interface_shutdown)
        INTERFACE_REDIRECTS = (Optional(Literal("no")) + Literal("ip") + Literal("redirects")).setParseAction(self.on_interface_redirects)
        INTERFACE_PROXY_ARP = (Optional(Literal("no")) + Literal("ip") + Literal("proxy-arp")).setParseAction(self.on_interface_proxy_arp)
        INTERFACE_SPEED = Literal("speed") + ALPHANUMS.copy().setParseAction(self.on_interface_speed)
        INTERFACE_DUPLEX = Literal("duplex") + ALPHANUMS.copy().setParseAction(self.on_interface_duplex)
        INTERFACE_UNTAGGED = Literal("switchport") + Literal("access") + Literal("vlan") + DIGITS.copy().setParseAction(self.on_interface_untagged)
        INTERFACE_TAGGED = (
            Literal("switchport") + Literal("trunk") +
            Literal("allowed") + Literal("vlan") +
            REST.copy().setParseAction(self.on_interface_tagged)
        )
        INTERFACE_CDP = (Optional(Literal("no")) + Literal("cdp") + Literal("enable")).setParseAction(self.on_interface_cdp)
        INTERFACE_BLOCK = INTERFACE + ZeroOrMore(INDENT + (
            INTERFACE_DESCRIPTION |
            INTERFACE_ADDRESS |
            INTERFACE_SHUTDOWN |
            INTERFACE_REDIRECTS |
            INTERFACE_PROXY_ARP |
            INTERFACE_SPEED |
            INTERFACE_DUPLEX |
            INTERFACE_UNTAGGED |
            INTERFACE_TAGGED |
            INTERFACE_CDP |
            LINE
        ))
        # Logging
        LOGGING_HOST = LineStart() + Literal("logging") + IPv4_ADDRESS.copy().setParseAction(self.on_logging_host)
        LOGGING_BLOCK = LOGGING_HOST
        # NTP
        NTP_SERVER = LineStart() + Literal("ntp") + Literal("server") + IPv4_ADDRESS.copy().setParseAction(self.on_ntp_server)
        NTP_BLOCK = NTP_SERVER

        CONFIG = (
            SYSTEM_BLOCK |
            VLAN_RANGE |
            VLAN_BLOCK |
            INTERFACE_BLOCK |
            LOGGING_BLOCK |
            NTP_BLOCK
        )
        return CONFIG

    def get_interface_defaults(self, name):
        r = {
            "admin_status": False,
            "protocols": []
        }
        # @todo: Replace with more reliable type detection
        if self.enable_cdp and name[:2] in ("Fa", "Gi", "Te"):
            r["protocols"] += ["CDP"]
        return r

    def get_subinterface_defaults(self):
        return {
            "ip_redirects": True,
            "ip_proxy_arp": True
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

    def on_nameserver(self, tokens):
        self.get_system_fact().nameservers += [tokens[0]]

    def on_user(self, tokens):
        tokens = list(tokens)
        user = self.get_user_fact(tokens[0])
        if "privilege" in tokens:
            i = tokens.index("privilege")
            user.level = int(tokens[i + 1])

    def on_cdp_run(self, tokens):
        self.enable_cdp = tokens[0] != "no"

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

    def on_interface_cdp(self, tokens):
        if tokens[0] == "no":
            self.get_current_interface().remove_protocol("CDP")
        else:
            self.get_current_interface().add_protocol("CDP")

    def on_interface_redirects(self, tokens):
        self.get_current_subinterface().ip_redirects = tokens[0] != "no"

    def on_interface_proxy_arp(self, tokens):
        self.get_current_subinterface().ip_proxy_arp = tokens[0] != "no"

    def on_interface_speed(self, tokens):
        self.get_current_interface().speed = tokens[-1]

    def on_interface_duplex(self, tokens):
        self.get_current_interface().duplex = tokens[-1]

    def on_interface_untagged(self, tokens):
        self.get_current_subinterface().untagged_vlan = int(tokens[0])

    def on_interface_tagged(self, tokens):
        vlans = tokens[0].strip()
        if vlans.startswith("add"):
            vlans = vlans.split(" ", 1)[1].strip()
        si = self.get_current_subinterface()
        for v in ranges_to_list(vlans):
            si.tagged_vlans += [int(v)]

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