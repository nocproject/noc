# ---------------------------------------------------------------------
# phone.phonerange application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.inv.models.resourcegroup import ResourceGroup
from noc.phone.models.phonerange import PhoneRange
from noc.services.web.base.decorators.state import state_handler
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


@state_handler
class PhoneRangeApplication(ExtDocApplication):
    """
    PhoneRange application
    """

    title = "Phone Range"
    menu = [_("Phone Ranges")]
    model = PhoneRange
    parent_model = PhoneRange
    parent_field = "parent"
    query_fields = ["name__icontains", "description__icontains", "from_number__startswith"]
    resource_group_fields = [
        "static_service_groups",
        "effective_service_groups",
        "static_client_groups",
        "effective_client_groups",
    ]

    def field_total_numbers(self, o):
        return o.total_numbers

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": smart_text(o), "has_children": o.has_children}

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

    @view("^(?P<id>[0-9a-f]{24})/get_path/$", access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(PhoneRange, id=id)
        path = [PhoneRange.get_by_id(r) for r in o.get_path()]
        return {
            "data": [
                {"id": str(p.id), "level": path.index(p) + 1, "label": smart_text(p.name)}
                for p in path
            ]
        }

    def get_Q(self, request, query):
        q = super().get_Q(request, query)
        q |= Q(from_number__lte=query, to_number__gte=query)
        return q
