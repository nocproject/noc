# ----------------------------------------------------------------------
# sa.service application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.lib.app.decorators.state import state_handler
from noc.sa.models.service import Service
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.translation import ugettext as _
from noc.core.validators import is_objectid
from noc.core.comp import smart_text


@state_handler
class ServiceApplication(ExtDocApplication):
    """
    Service application
    """

    title = "Services"
    menu = [_("Services")]
    model = Service
    parent_model = Service
    parent_field = "parent"
    query_fields = ["id", "description"]

    resource_group_fields = [
        "static_service_groups",
        "effective_service_groups",
        "static_client_groups",
        "effective_client_groups",
    ]

    def get_Q(self, request, query):
        if is_objectid(query):
            q = Q(id=query)
        else:
            q = super().get_Q(request, query)
        return q

    def instance_to_dict(self, o, fields=None, nocustom=False):
        def sg_to_list(items):
            return [
                {"group": str(x), "group__label": smart_text(ResourceGroup.get_by_id(x))}
                for x in items
            ]

        data = super().instance_to_dict(o, fields, nocustom)
        # Expand resource groups fields
        for fn in self.resource_group_fields:
            data[fn] = sg_to_list(data.get(fn) or [])
        return data

    def clean(self, data):
        # Clean resource groups
        for fn in self.resource_group_fields:
            if fn.startswith("effective_") and fn in data:
                del data[fn]
                continue
            data[fn] = [x["group"] for x in (data.get(fn) or [])]
        # Clean other
        return super().clean(data)
