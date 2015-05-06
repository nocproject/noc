## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip_discovery helpers
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.template import Template, Context
## NOC modules
from noc.lib.ip import IP
from noc.settings import config


## Compile FQDN template
t = config.get("ip_discovery", "fqdn_template")
fqdn_template = Template(t) if t else None


def get_fqdn(interface, vrf, address, ctx):
    """
    Generate FQDN for address.
    Called by ipreport.py to determine FQDN for the found address.
    Default behavior is to apply variables to
    [ip_discovery]/fqdn_template
    :param managed_object: Managed Object instance
    :param interface: Normalized interface name
    :param vrf: VRF instance
    :param address: IPv4/IPv6 address ass string
    :param ctx: Object context
    :return: FQDN
    """
    afi = IP.get_afi(address)
    # Per-octet, direct order
    if afi == "4":
        ip = [str(x) for x in IP.prefix(address)._get_parts()]
    else:
        ip = ["%x" % x for x in IP.prefix(address)._get_parts()]
    # Per-octet, reversed order
    rip = list(reversed(ip))
    # Apply default context
    c = ctx.copy()
    # Update calculated variables
    c.update({
        "afi": afi,
        "IP": ip,
        "rIP": rip,
        "interface": interface,
        "vrf": vrf
    })
    # Generate FQDN
    return fqdn_template.render(Context(c))


def get_description(object, interface):
    """
    Generate description for address
    Called by ipreport.py to determine description for the found address
    :param object: Managed object instance
    :param name: Normalized interface name
    """
    return "Seen at %s:%s" % (object.name, interface)
