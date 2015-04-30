# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic IOS XR parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Third-party modules
from pyparsing import OneOrMore, Word, alphanums, QuotedString
## NOC modules
from noc.cm.parsers.base import BaseParser
from noc.lib.validators import is_ipv4, is_ipv6


class BaseIOSXRParser(BaseParser):
    rx_indent = re.compile(r"^(\s*)")

    def __init__(self, managed_object):
        super(BaseIOSXRParser, self).__init__(managed_object)

    def parse(self, config):
        VALUE = OneOrMore(Word(alphanums + "-/.:_+") | QuotedString("'"))
        context = []
        indent = []
        for l in config.splitlines():
            ls = l.strip()
            if not ls or ls.startswith("!"):
                continue  # Comment line
            match = self.rx_indent.search(l)
            ilevel = len(match.group(1))
            if not indent:
                indent = [ilevel]
                context = [ls]
            elif indent[-1] == ilevel:
                # Same level context
                context = context[:-1] + [ls]
            elif indent[-1] < ilevel:
                # Down
                context += [ls]
                indent += [ilevel]
            else:
                # Up
                while indent and indent[-1] >= ilevel:
                    indent.pop(-1)
                    context.pop(-1)
                context += [ls]
                indent += [ilevel]
            cp = " ".join(context).split()
            h = self.handlers
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
        r = super(BaseIOSXRParser, self).get_interface_defaults(name)
        r["admin_status"] = True
        return r

    def on_hostname(self, tokens):
        """
        hostname <name>
        """
        self.get_system_fact().hostname = tokens[1]

    def on_timezone(self, tokens):
        """
        clock timezone MSK 3
        """
        self.get_system_fact().timezone = " ".join(tokens[2:])

    def on_domain_name(self, tokens):
        """
        domain name <domain>
        """
        self.get_system_fact().domain_name = tokens[2]

    def on_domain_name_server(self, tokens):
        """
        domain name-server <server>
        """
        self.get_system_fact().nameservers += [tokens[2]]

    def on_ntp_server(self, tokens):
        """
        ntp
         server <server> prefer
         server <server>
        """
        self.get_ntpserver_fact(tokens[2])

    def on_syslog_server(self, tokens):
        """
        logging <server>
        """
        h = tokens[1]
        if is_ipv4(h) or is_ipv6(h):
            self.get_sysloghost_fact(h)

    handlers = {
        "hostname": on_hostname,
        "clock": {
            "timezone": on_timezone
        },
        "domain": {
            "name": on_domain_name,
            "name-server": on_domain_name_server
        },
        "ntp": {
            "server": on_ntp_server
        },
        "logging": on_syslog_server
    }
