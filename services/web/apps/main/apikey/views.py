# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.apikey application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.apikey import APIKey
from noc.core.translation import ugettext as _


class APIKeyApplication(ExtDocApplication):
    """
    APIKey application
    """
    title = "API Key"
    menu = [_("Setup"), _("API Keys")]
    model = APIKey
    glyph = "key"
