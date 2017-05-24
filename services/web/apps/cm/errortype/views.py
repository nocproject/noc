# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# cm.errortype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.cm.models.errortype import ErrorType
from noc.core.translation import ugettext as _


class ErrorTypeApplication(ExtDocApplication):
    """
    ErrorType application
    """
    title = _("Error Type")
    menu = [_("Setup"), _("Error Types")]
    model = ErrorType
