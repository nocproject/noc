# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# dns.dnszoneprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.dns.models.dnszoneprofile import DNSZoneProfile
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication


class DNSZoneProfileApplication(ExtModelApplication):
    """
    DNSZoneProfiles application
    """
    title = _("Zone Profiles")
    menu = [_("Setup"), _("Zone Profiles")]
    model = DNSZoneProfile

    def field_masterslabel(self, o):
        return u", ".join([s.name for s in o.masters.all()])

    def field_slaveslabel(self, o):
        return u", ".join([s.name for s in o.slaves.all()])
