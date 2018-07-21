# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.audittrail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.audittrail import AuditTrail
from noc.core.translation import ugettext as _
from noc.models import get_object


class AuditTrailApplication(ExtDocApplication):
    """
    AuditTrails application
    """
    title = _("Audit Trail")
    menu = _("Audit Trail")
    model = AuditTrail
    query_fields = ["model_id", "user"]

    def field_object_name(self, o):
        return unicode(get_object(o.model_id, o.object))
