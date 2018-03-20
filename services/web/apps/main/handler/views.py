# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.handler application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.handler import Handler
from noc.core.translation import ugettext as _


class HandlerApplication(ExtDocApplication):
    """
    Handler application
    """
    title = "Handler"
    menu = [_("Setup"), _("Handlers")]
    model = Handler
