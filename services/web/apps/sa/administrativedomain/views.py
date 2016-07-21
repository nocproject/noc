# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.administrativedomain application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _


class AdministrativeDomainApplication(ExtModelApplication):
    """
    AdministrativeDomain application
    """
    title = _("Administrative Domains")
    menu = [_("Setup"), _("Administrative Domains")]
    model = AdministrativeDomain
    query_fields = ["name__icontains", "description__icontains"]

    def field_object_count(self, o):
        return o.managedobject_set.count()
