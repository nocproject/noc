# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.profilecheckrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sa.models.profilecheckrule import ProfileCheckRule


class ProfileCheckRuleApplication(ExtDocApplication):
    """
    ProfileCheckRule application
    """
    title = _("Profile Check Rule")
    menu = [_("Setup"), _("Profile Check Rules")]
    model = ProfileCheckRule
    query_fields = ["name__icontains", "description__icontains", "value__icontains"]
