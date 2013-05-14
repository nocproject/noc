# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.audittrail application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models.audittrail import AuditTrail


class AuditTrailApplication(ExtModelApplication):
    """
    AuditTrails application
    """
    title = "Audit Trail"
    menu = "Audit Trail"
    model = AuditTrail
    query_fields = ["subject__icontains", "body__icontains"]

