# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefixaccess application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.ip.models import PrefixAccess
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication


class PrefixAccessApplication(ExtModelApplication):
    """
    PrefixAccess application
    """
    title = _("Prefix Access")
    menu = [_("Setup"), _("Prefix Access")]
    model = PrefixAccess
    query_fields = ["user__username", "prefix"]
    query_condition = "icontains"
