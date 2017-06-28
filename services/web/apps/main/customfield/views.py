# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.customfield application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.main.models import CustomField
from noc.core.translation import ugettext as _


class CustomFieldApplication(ExtModelApplication):
    """
    CustomField application
    """
    title = _("Custom Fields")
    menu = [_("Setup"), _("Custom Fields")]
    model = CustomField
    icon = "icon_cog_add"
    query_fields = ["name", "description", "table"]
