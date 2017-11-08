# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# gis.division application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.gis.models.division import Division
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class DivisionApplication(ExtDocApplication):
    """
    Division application
    """
    title = _("Division")
    menu = [_("Setup"), _("Divisions")]
    model = Division
    parent_field = "parent"
    query_fields = ["name__icontains"]
    default_ordering = ["level", "name"]

    def field_full_parent(self, o):
        if o.parent:
            return o.parent.full_path
        else:
            return ""

    def field_full_path(self, o):
        return o.full_path

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": o.full_path
        }
