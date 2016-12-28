# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## phone.phonerange application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
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

    def field_total_numbers(self, o):
        return o.total_numbers

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": unicode(o),
            "has_children": o.has_children
        }

    @view("^(?P<id>\d+)/get_path/$",
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
