# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## dns.dnszoneprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.dns.models import DNSZoneProfile

class DNSZoneProfileApplication(ExtModelApplication):
    """
    DNSZoneProfiles application
    """
    title = "Zone Profiles"
    menu = "Setup | Zone Profiles"
    model = DNSZoneProfile

    def field_masterslabel(self, o):
        return u", ".join([s.name for s in o.masters.all()])

    def field_slaveslabel(self, o):
        return u", ".join([s.name for s in o.slaves.all()])

