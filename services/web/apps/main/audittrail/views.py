# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.audittrail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.main.models.audittrail import AuditTrail
from noc.core.translation import ugettext as _


class AuditTrailApplication(ExtDocApplication):
    """
    AuditTrails application
    """
    title = _("Audit Trail")
    menu = _("Audit Trail")
    model = AuditTrail
    query_fields = ["model_id", "user"]

