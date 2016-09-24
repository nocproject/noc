# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.objectlist application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess


class ObjectListApplication(ExtApplication):
    """
    ManagedObject application
    """
    model = ManagedObject

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        if request.user.is_superuser:
            return self.model.objects.filter(is_managed=True)
        else:
            return self.model.filter(
                is_managed=True,
                administrative_domain__in=UserAccess.get_domains(request.user)
            )

    def instance_to_dict(self, o, fields=None):
        return {
            "id": str(o.id),
            "name": o.name,
            "address": o.address,
            "profile_name": o.profile_name,
            "platform": o.platform,
            "row_class": o.object_profile.style.css_class_name if o.object_profile.style else ""
        }

    def cleaned_query(self, q):
        nq = {}
        for k in q:
            if not k.startswith("_"):
                nq[k] = q
        return nq

    @view(method=["GET"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)
