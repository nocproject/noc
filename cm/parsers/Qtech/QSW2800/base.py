# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic QSW2800 parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Third-party modules
from pyparsing import *
## NOC modules
from noc.core.ip import IPv4
from noc.cm.parsers.pyparser import BasePyParser
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST, DIGITS, ALPHANUMS, RD
from noc.lib.text import ranges_to_list
from noc.lib.validators import is_ipv4, is_int


class BaseQSW2800Parser(BasePyParser):
    def __init__(self, managed_object):
        super(BaseQSW2800Parser, self).__init__(managed_object)

    def create_parser(self):
        # System
        HOSTNAME = LineStart() + Literal("hostname") + REST.copy().setParseAction(self.on_hostname)
        TIMEZONE = LineStart() + Literal("clock timezone") + REST.copy().setParseAction(self.on_timezone)
        SERVICE = LineStart() + (Optional(Literal("no")) + Literal("service") + Word(alphanums + "-") + restOfLine).setParseAction(self.on_service)
        
        SYSTEM_BLOCK = (
            HOSTNAME |
            TIMEZONE |
            SERVICE 
        
        )

        # Logging
        LOGGING_HOST = LineStart() + Literal("logging") + IPv4_ADDRESS.copy().setParseAction(self.on_logging_host)
        LOGGING_BLOCK = LOGGING_HOST
        # NTP
        NTP_SERVER = LineStart() + Literal("ntp") + Literal("server") + IPv4_ADDRESS.copy().setParseAction(self.on_ntp_server)
        NTP_BLOCK = NTP_SERVER
                                                                 
                                               
        CONFIG = ZeroOrMore(
            SYSTEM_BLOCK |
            LOGGING_BLOCK |
            NTP_BLOCK
        )
        return CONFIG

    def get_user_defaults(self):
        return {
            "level": 0
        }

    def on_hostname(self, tokens):
        self.get_system_fact().hostname = tokens[0]

    def on_timezone(self, tokens):
        self.get_system_fact().timezone = tokens[0]

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

    def on_ntp_server(self, tokens):
        self.get_ntpserver_fact(tokens[0])

    def on_logging_host(self, tokens):
        self.get_sysloghost_fact(tokens[0])

        