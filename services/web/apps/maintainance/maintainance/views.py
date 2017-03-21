# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## maintainance.maintainance application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintainance.models.maintainance import Maintainance
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class MaintainanceApplication(ExtDocApplication):
    """
    Maintainance application
    """
    title = _("Maintainance")
    menu = _("Maintainance")
    model = Maintainance
    query_condition = "icontains"
    query_fields = ["subject"]

    @view(url="(?P<id>[0-9a-f]{24})/objects/", method=["GET"],
          access="read", api=True)
    def api_test(self, request, id):
        o = self.get_object_or_404(Maintainance, id=id)
        return [
            {
                "id": mo.id,
                "name": mo.name,
                "is_managed": mo.is_managed,
                "profile": mo.profile_name,
                # "platform": mo.platform,
                # "administrative_domain": unicode(mo.administrative_domain),
                "address": mo.address,
                "description": mo.description,
                "tags": mo.tags
            } for mo in ManagedObject.objects.filter(id__in=o.currently_affected)
        ]
