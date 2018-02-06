# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.phonerange application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.queryset import Q
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.phone.models.phonerange import PhoneRange
from noc.core.translation import ugettext as _


class PhoneRangeApplication(ExtDocApplication):
    """
    PhoneRange application
    """
    title = "Phone Range"
    menu = [_("Phone Ranges")]
    model = PhoneRange
    parent_model = PhoneRange
    parent_field = "parent"
    query_fields = [
        "name__icontains",
        "description__icontains",
        "from_number__startswith"
    ]

    def field_total_numbers(self, o):
        return o.total_numbers

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": unicode(o),
            "has_children": o.has_children
        }

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    @view("^(?P<id>[0-9a-f]{24})/get_path/$",
          access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(PhoneRange, id=id)
        path = [PhoneRange.get_by_id(r) for r in o.get_path()]
        return {
            "data": [{
                "id": str(p.id),
                "level": path.index(p) + 1,
                "label": unicode(p.name)
            } for p in path]
        }

    def get_Q(self, request, query):
        q = super(PhoneRangeApplication, self).get_Q(request, query)
        q |= Q(from_number__lte=query, to_number__gte=query)
        return q
