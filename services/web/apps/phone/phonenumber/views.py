# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.phonenumber application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.phone.models.phonenumber import PhoneNumber
from noc.core.translation import ugettext as _


class PhoneNumberApplication(ExtDocApplication):
    """
    PhoneNumber application
    """
    title = "Phone Number"
    menu = [_("Phone Number")]
    model = PhoneNumber
    query_fields = [
        "number__contains",
        "description__icontains"
    ]

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": unicode(o),
            "dialplan": o.dialplan.name
        }

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""
