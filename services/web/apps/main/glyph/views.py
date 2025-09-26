# ----------------------------------------------------------------------
# main.glyph application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.main.models.glyph import Glyph
from noc.core.translation import ugettext as _
from noc.core.comp import smart_text


class GlyphApplication(ExtDocApplication):
    """
    Glyph application
    """

    title = "Glyph"
    menu = [_("Setup"), _("Glyphs")]
    model = Glyph
    glyph = "font-awesome"
    query_condition = "icontains"

    def instance_to_lookup(self, o: Glyph, fields=None):
        return {"id": str(o.id), "label": smart_text(o), "code": o.code, "font": o.font.font_family}
