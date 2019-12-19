# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.managedobjectselector application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.sa.models.managedobjectselector import (
    ManagedObjectSelector,
    ManagedObjectSelectorByAttribute,
)
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


class ManagedObjectSelectorApplication(ExtModelApplication):
    """
    ManagedObjectSelector application
    """

    title = _("Managed Object Selector")
    menu = [_("Setup"), _("Managed Object Selector")]
    model = ManagedObjectSelector
    query_fields = ["name__icontains", "description__icontains"]
    attrs = ModelInline(ManagedObjectSelectorByAttribute)

    def field_expression(self, o):
        return o.expr

    def cleaned_query(self, q):
        if q.get("id__referred") == "sa.managedobject__selector":
            del q["id__referred"]
        return super(ManagedObjectSelectorApplication, self).cleaned_query(q)

    @view(url=r"(?P<id>\d+)/objects/", method=["GET"], access="read", api=True)
    def api_test(self, request, id):
        o = self.get_object_or_404(ManagedObjectSelector, id=int(id))
        return [
            {
                "id": mo.id,
                "name": mo.name,
                "is_managed": mo.is_managed,
                "profile": mo.profile.name,
                "platform": mo.platform.name if mo.platform else "",
                "administrative_domain": smart_text(mo.administrative_domain),
                "address": mo.address,
                "description": mo.description,
                "tags": mo.tags,
            }
            for mo in o.managed_objects
        ]
