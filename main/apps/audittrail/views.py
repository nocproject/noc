# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.audittrail application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.main.models.audittrail import AuditTrail


class AuditTrailApplication(ExtDocApplication):
    """
    AuditTrails application
    """
    title = "Audit Trail"
    menu = "Audit Trail"
    model = AuditTrail

