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
        VALUE = OneOrMore(Word(alphanums + "-/.:_+[]") | QuotedString("\""))
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

    def iter_group(self, tokens):
        if tokens and tokens[0] == "[" and tokens[-1] == "]":
            for t in tokens[1:-1]:
                yield t
        else:
            for t in tokens:
                yield t

    def get_interface_defaults(self, name):
        r = super(BaseJUNOSParser, self).get_interface_defaults(name)
        r["admin_status"] = True
        return r

    def get_subinterface_fact(self, name, interface=None):
        if "." in name and interface is None:
            interface = name.split(".")[0]
        si = super(BaseJUNOSParser, self).get_subinterface_fact(name, interface)
        si.admin_status = True
        return si

    def get_isis_subinterface_fact(self, name):
        """
        Get subinterface fact with default ISIS settings
        """
        si = self.get_subinterface_fact(name)
        si.add_protocol("ISIS")
        return si

    def get_ospf_subinterface_fact(self, name):
        """
        Get subinterface fact with default ISIS settings
        """
        si = self.get_subinterface_fact(name)
        si.add_protocol("OSPF")
        return si

    def get_ldp_subinterface_fact(self, name):
        """
        Get subinterface fact with default ISIS settings
        """
        si = self.get_subinterface_fact(name)
        si.add_protocol("LDP")
        return si

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

    def on_subinterface_iso(self, tokens):
        """
        set interface <N> unit <M> family iso
        """
        self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3])).add_afi("ISO")

    def on_subinterface_mpls(self, tokens):
        """
        set interface <N> unit <M> family mpls
        """
        self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3])).add_afi("MPLS")

    def on_subinterface_ipv4_address(self, tokens):
        """
        set interface <N> unit <M> family inet address <K>
        """
        si = self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3]))
        si.ipv4_addresses += [tokens[7]]
        si.add_afi("IPv4")

    def on_subinterface_ipv6_address(self, tokens):
        """
        set interface <N> unit <M> family inet6 address <K>
        """
        si = self.get_subinterface_fact("%s.%s" % (tokens[1], tokens[3]))
        si.ipv6_addresses += [tokens[7]]
        si.add_afi("IPv6")

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
        self.get_isis_subinterface_fact(tokens[3]).isis_ptp = True

    def on_isis_interface_metric(self, tokens):
        """
        set protocols isis interface <N> level <M> metric <K>
        """
        si = self.get_isis_subinterface_fact(tokens[3])
        if tokens[5] == "1":
            si.isis_l1_metric = int(tokens[7])
        else:
            si.isis_l2_metric = int(tokens[7])

    def on_ldp_interface(self, tokens):
        """
        set protocols ldp interface <N>
        """
        self.get_ldp_subinterface_fact(tokens[3])

    def on_pim_interface(self, tokens):
        """
        set protocols pim interface <N>
        set protocols pim interface <N> mode <sparse|dense>
        set protocols pim interface <N> version 2
        """
        si = self.get_subinterface_fact(tokens[3])
        cmd = tokens[4] if len(tokens) > 4 else None
        if cmd == "mode":
            si.pim_mode = tokens[5]
        elif cmd == "version":
            si.pim_version = tokens[5]
        elif cmd is None:
            si.pim_version = "2"
            si.pim_mode = "sparse"
        si.add_protocol("PIM")

    def on_static_route(self, tokens):
        """
        set routing-options static route <N> next-hop <NH>
        set routing-options static route <N> discard
        set routing-options static route <N> tag <N>
        set routing-options static route <N> preference <N>
        set routing-options static route <N> community [c1 c2 cN]
        """
        prefix = tokens[3]
        cmd = tokens[4] if len(tokens) >= 4 else None
        if cmd == "next-hop":
            for nh in self.iter_group(tokens[5:]):
                self.get_static_route_fact(prefix).next_hop = nh
        elif cmd == "discard":
            self.get_static_route_fact(prefix).discard = True
        elif cmd == "tag":
            self.get_static_route_fact(prefix).tag = int(tokens[5])
        elif cmd == "preference":
            self.get_static_route_fact(prefix).distance = int(tokens[5])

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
                            },
                            "inet6": {
                                "address": on_subinterface_ipv6_address
                            },
                            "iso": on_subinterface_iso,
                            "mpls": on_subinterface_mpls
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
            },
            "ldp": {
                "interface": {
                    "*": on_ldp_interface
                }
            },
            "pim": {
                "interface": {
                    "*": on_pim_interface
                }
            }
        },
        "routing-options": {
            "static": {
                "route": {
                    "*": on_static_route
                }
            }
        },
        "snmp": {
            "contact": on_snmp_contact
        }
    }
