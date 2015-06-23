# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.managedobjectselector application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.sa.models.managedobjectselector import (
    ManagedObjectSelector, ManagedObjectSelectorByAttribute)


class ManagedObjectSelectorApplication(ExtModelApplication):
    """
    ManagedObjectSelector application
    """
    title = "Managed Object Selector"
    menu = "Setup | Managed Object Selector"
    model = ManagedObjectSelector
    query_fields = ["name__icontains", "description__icontains"]
    attrs = ModelInline(ManagedObjectSelectorByAttribute)

    def field_expression(self, o):
        return o.expr

    def cleaned_query(self, q):
        if q.get("id__referred") == "sa.managedobject__selector":
            del q["id__referred"]
        return super(ManagedObjectSelectorApplication, self).cleaned_query(q)

    @view(url="(?P<id>\d+)/objects/", method=["GET"],
          access="read", api=True)
    def api_test(self, request, id):
        o = self.get_object_or_404(ManagedObjectSelector, id=int(id))
        return [
            {
                "id": mo.id,
                "name": mo.name,
                "is_managed": mo.is_managed,
                "profile": mo.profile_name,
                "platform": mo.platform,
                "administrative_domain": unicode(mo.administrative_domain),
                "address": mo.address,
                "description": mo.description,
                "tags": mo.tags
            } for mo in o.managed_objects
        ]