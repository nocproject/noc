# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.division application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.gis.models.street import Street


class StreetApplication(ExtDocApplication):
    """
    Street application
    """
    title = "Street"
    menu = "Setup | Streets"
    model = Street
    query_fields = ["name__icontains"]

    def field_full_parent(self, o):
        return o.full_path

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": o.full_path
        }
