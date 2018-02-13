# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefixaccess application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models.prefixaccess import PrefixAccess
from noc.core.translation import ugettext as _


class PrefixAccessApplication(ExtModelApplication):
    """
    PrefixAccess application
    """
    title = _("Prefix Access")
    menu = [_("Setup"), _("Prefix Access")]
    model = PrefixAccess
    query_fields = ["user__username", "prefix"]
    query_condition = "icontains"
