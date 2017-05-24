# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# dns.dnsserver application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.dns.models.dnsserver import DNSServer
from noc.core.translation import ugettext as _


class DNSServerApplication(ExtModelApplication):
    """
    DNSServer application
    """
    title = _("DNS Server")
    menu = [_("Setup"), _("DNS Servers")]
    model = DNSServer
