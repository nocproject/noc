# ---------------------------------------------------------------------
# gis.layer application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.gis.models.layer import Layer
from noc.sa.interfaces.base import ColorParameter
from noc.core.translation import ugettext as _


class LayerApplication(ExtDocApplication):
    """
    Layer application
    """

    title = _("Layers")
    menu = [_("Setup"), _("Layers")]
    model = Layer
    clean_fields = {"stroke_color": ColorParameter(), "fill_color": ColorParameter()}
    query_fields = ["name__icontains", "description__icontains"]
