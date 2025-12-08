# ---------------------------------------------------------------------
# phone.phonenumber application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.services.web.base.decorators.state import state_handler
from noc.inv.models.resourcegroup import ResourceGroup
from noc.phone.models.phonenumber import PhoneNumber
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


@state_handler
class PhoneNumberApplication(ExtDocApplication):
    """
    PhoneNumber application
    """

    title = "Phone Number"
    menu = [_("Phone Number")]
    model = PhoneNumber
    query_fields = ["number__contains", "description__icontains"]
    resource_group_fields = [
        "static_service_groups",
        "effective_service_groups",
        "static_client_groups",
        "effective_client_groups",
    ]

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": smart_text(o), "dialplan": o.dialplan.name}

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
