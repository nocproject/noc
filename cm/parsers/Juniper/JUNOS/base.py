# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic Junos parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from collections import defaultdict
## Third-party modules
from pyparsing import OneOrMore, Word, alphanums, QuotedString
## NOC modules
from noc.lib.ip import IPv4
from noc.cm.parsers.base import BaseParser
from noc.cm.parsers.tokens import INDENT, IPv4_ADDRESS, LINE, REST, DIGITS, ALPHANUMS
from noc.lib.text import ranges_to_list


class BaseJUNOSParser(BaseParser):

    def __init__(self, managed_object):
        super(BaseJUNOSParser, self).__init__(managed_object)

    def parse(self, config):
        VALUE = OneOrMore(Word(alphanums + "-/.:_+") | QuotedString("\""))
        context = []
        inactive_level = None
        for l in config.splitlines():
            # @todo: Skip inactive blocks
            if "##" in l:
                l = l.split("##", 1)[0]
            l = l.strip()
            if l == "{master}":
                continue
            elif l.startswith("inactive:"):
                if l.endswith("{"):
                    inactive_level = len(context)
                    context += [l[9:-1].strip()]
            elif l.startswith("/*"):
                continue
            elif l.endswith("{"):
                context += [l[:-1].strip()]
            elif l == "}":
                context.pop(-1)
                if inactive_level is not None and inactive_level >= len(context):
                    inactive_level = None
            elif l.endswith(";"):
                if inactive_level is not None:
                    continue
                cp = " ".join(context).split() + l[:-1].split()
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

    def get_subinterface_fact(self, name, interface=None):
        if "." in name and interface is None:
            interface = name.split(".")[0]
        return super(BaseJUNOSParser, self).get_subinterface_fact(name, interface)

    def on_system_host_name(self, tokens):
        """
        set system host-name <hostname>
        """
        self.get_system_fact().hostname = tokens[-1]

    def on_system_domain_name(self, tokens):
        """
        set system domain-name <name>
        """
        self.get_system_fact().domain_name = tokens[-1]

    def on_system_time_zone(self, tokens):
        """
        set system time-zone <tz>
        """
        self.get_system_fact().timezone = tokens[-1]

    def on_system_name_server(self, tokens):
        """
        set system name-server <N>
        """
        self.get_system_fact().nameservers += [tokens[-1]]

    def on_system_login_user_class(self, tokens):
        """
        set system login user <user> class <class>
        """
        self.get_user_fact(tokens[3]).groups += [tokens[-1]]

    def on_system_ntp_server(self, tokens):
        """
        set system ntp server <N>
        """
        self.get_ntpserver_fact(tokens[-1])

    def on_interfaces_description(self, tokens):
        """
        set interfaces <N> description "<description>"
        """
        self.get_interface_fact(tokens[1]).description = tokens[-1]

    def on_interface_aggregated(self, tokens):
        """
        set interfaces <N> gigether-options 802.3ad ae<N>
        """
        a_iface = tokens[4]
        iface = self.get_interface_fact(tokens[1])
        if a_iface.startswith("ae"):
            iface.aggregated_interface = a_iface

    def on_subinterface_description(self, tokens):
        """
        set interface <N> unit <M> description "<K>"
        """
        self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3])).description = tokens[-1]

    def on_subinterface_vlan_id(self, tokens):
        """
        set interface <N> unit <M> vlan-id <K>
        """
        si = self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3]))
        si.vlan_ids = [tokens[-1]]

    def on_subinterface_ipv4_address(self, tokens):
        """
        set interface <N> unit <M> family inet address <K>
        """
        si = self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3]))
        si.ipv4_addresses += [tokens[7]]
        si.add_afi("IPv4")

    def on_subinterface_ipv4_filter(self, tokens):
        """
        set interface <N> unit <M> family inet filter {input|output} <K>
        """
        si = self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3]))
        if tokens[7].startswith("input"):
            si.input_ipv4_filter = tokens[8]
        else:
            si.output_ipv4_filter = tokens[8]

    def on_isis_interface_ptp(self, tokens):
        """
        set protocols isis interface <N> point-to-point
        """
        si = self.get_subinterface_fact(tokens[3])
        si.isis_ptp = True
        si.add_afi("ISO")

    def on_isis_interface_metric(self, tokens):
        """
        set protocols isis interface <N> level <M> metric <K>
        """
        si = self.get_subinterface_fact(tokens[3])
        si.add_afi("ISO")
        if tokens[5] == "1":
            si.isis_l1_metric = int(tokens[7])
        else:
            si.isis_l2_metric = int(tokens[7])

    def on_snmp_contact(self, tokens):
        """
        set snmp contact <N>
        """
        pass

    handlers = {
        "system": {
            "host-name": on_system_host_name,
            "domain-name": on_system_domain_name,
            "time-zone": on_system_time_zone,
            "name-server": on_system_name_server,
            "login": {
                "user": {
                    "*": {
                        "class": on_system_login_user_class
                    }
                }
            },
            "ntp": {
                "server": on_system_ntp_server
            }
        },
        "interfaces": {
            "*": {
                "description": on_interfaces_description,
                "gigether-options": {
                    "802.3ad": on_interface_aggregated
                },
                "unit": {
                    "*": {
                        "description": on_subinterface_description,
                        "vlan-id": on_subinterface_vlan_id,
                        "family": {
                            "inet": {
                                "address": on_subinterface_ipv4_address,
                                "filter": {
                                    "*": on_subinterface_ipv4_filter
                                }
                            }
                        }
                    }
                }
            }
        },
        "protocols": {
            "isis": {
                "interface": {
                    "*": {
                        "point-to-point": on_isis_interface_ptp,
                        "level": {
                            "*": {
                                "metric": on_isis_interface_metric
                            }
                        }
                    }
                }
            }
        },
        "snmp": {
            "contact": on_snmp_contact
        }
    }
