# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.division application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.gis.models.division import Division


class DivisionApplication(ExtDocApplication):
    """
    Division application
    """
    title = "Division"
    menu = "Setup | Divisions"
    model = Division
    query_fields = ["name__icontains"]

    def full_path(self, o):
        if not o.parent:
            return ""
        r = [unicode(o.parent)]
        p = o.parent.parent
        while p:
            r = [unicode(p)] + r
            p = p.parent
        return " | ".join(r)

    def field_full_parent(self, o):
        return self.full_path(o)

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": self.full_path(o)
        }
