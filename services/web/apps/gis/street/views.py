# ---------------------------------------------------------------------
# gis.division application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.gis.models.division import Division
from noc.gis.models.street import Street
from noc.core.translation import ugettext as _


class StreetApplication(ExtDocApplication):
    """
    Street application
    """

    title = _("Street")
    menu = [_("Setup"), _("Streets")]
    model = Street
    parent_model = Division
    parent_field = "parent"
    query_fields = ["name__icontains"]
    default_ordering = ["parent", "name"]

    def field_full_parent(self, o):
        if o.parent:
            return o.parent.full_path
        return ""

    def field_full_path(self, o):
        return o.full_path

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": o.full_path}
