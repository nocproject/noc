# ---------------------------------------------------------------------
# dns.dnszone application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.services.web.base.modelinline import ModelInline
from noc.services.web.base.repoinline import RepoInline
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
