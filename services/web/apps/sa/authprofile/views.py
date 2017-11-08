# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.authprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.lib.app.modelinline import ModelInline
from noc.sa.models.authprofile import (
    AuthProfile, AuthProfileSuggestSNMP, AuthProfileSuggestCLI)


class AuthProfileApplication(ExtModelApplication):
    """
    AuthProfile application
    """
    title = _("Auth Profile")
    menu = [_("Setup"), _("Auth Profiles")]
    model = AuthProfile

    suggest_snmp = ModelInline(AuthProfileSuggestSNMP)
    suggest_cli = ModelInline(AuthProfileSuggestCLI)
