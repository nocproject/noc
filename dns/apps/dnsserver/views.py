# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## dns.dnsserver application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.dns.models import DNSServer


class DNSServerApplication(ExtModelApplication):
    """
    DNSServer application
    """
    title = "DNS Server"
    menu = "Setup | DNS Servers"
    model = DNSServer
