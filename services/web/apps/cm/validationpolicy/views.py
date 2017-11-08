# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# cm.validationpolicy application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.cm.models.validationpolicy import ValidationPolicy
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class ValidationPolicyApplication(ExtDocApplication):
    """
    ValidationPolicy application
    """
    title = _("Validation Policy")
    menu = [_("Setup"), _("Validation Policy")]
    model = ValidationPolicy
