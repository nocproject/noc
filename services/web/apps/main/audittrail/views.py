# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.audittrail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.audittrail import AuditTrail


class AuditTrailApplication(ExtDocApplication):
    """
    AuditTrails application
    """
    title = _("Audit Trail")
    menu = _("Audit Trail")
    model = AuditTrail
    query_fields = ["model_id", "user"]
