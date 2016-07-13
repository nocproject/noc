# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.layer application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.gis.models.layer import Layer
from noc.main.models.collectioncache import CollectionCache
from noc.sa.interfaces.base import ColorParameter
from noc.core.translation import ugettext as _


class LayerApplication(ExtDocApplication):
    """
    Layer application
    """
    title = _("Layers")
    menu = [_("Setup"), _("Layers")]
    model = Layer

    clean_fields = {
        "stroke_color": ColorParameter(),
        "fill_color": ColorParameter()
    }

    query_fields = ["name__icontains", "description__icontains"]

    def field_stroke_color(self, o):
        if o is None:
            return None
        else:
            return "%06X" % o.stroke_color

    def field_fill_color(self, o):
        if o is None:
            return None
        else:
            return "%06X" % o.fill_color
