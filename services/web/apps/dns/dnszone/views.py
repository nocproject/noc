# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# dns.dnszone application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.lib.app.repoinline import RepoInline
from noc.dns.models.dnszone import DNSZone
from noc.dns.models.dnszonerecord import DNSZoneRecord
from noc.core.translation import ugettext as _


class DNSZoneApplication(ExtModelApplication):
    """
    DNSZone application
    """
    title = _("DNS Zone")
    menu = _("Zones")
    model = DNSZone
    query_condition = "icontains"

    records = ModelInline(DNSZoneRecord)
    zone = RepoInline("zone")

    @view(url="^(?P<zone_id>\d+)/text/$", method=["GET"],
          access="read", api=True)
    def api_text(self, request, zone_id):
        zone = self.get_object_or_404(DNSZone, id=int(zone_id))
        return zone.get_zone_text()
