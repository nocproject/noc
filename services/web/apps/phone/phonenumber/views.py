# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.phonenumber application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.inv.models.resourcegroup import ResourceGroup
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
    resource_group_fields = [
        "static_service_groups",
        "effective_service_groups",
        "static_client_groups",
        "effective_client_groups"
    ]

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": unicode(o),
            "dialplan": o.dialplan.name
        }

    def instance_to_dict(self, o, fields=None, nocustom=False):
        def sg_to_list(items):
            return [
                {
                    "group": x,
                    "group__label": unicode(ResourceGroup.get_by_id(x))
                } for x in items
            ]

        data = super(PhoneNumberApplication, self).instance_to_dict(o, fields, nocustom)
        # Expand resource groups fields
        for fn in self.resource_group_fields:
            data[fn] = sg_to_list(data.get(fn) or [])
        return data

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""
