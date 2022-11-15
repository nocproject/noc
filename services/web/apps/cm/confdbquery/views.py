# ----------------------------------------------------------------------
# cm.confdbquery application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.cm.models.confdbquery import ConfDBQuery
from noc.core.confdb.engine.base import Engine
from noc.core.translation import ugettext as _


class ConfDBQueryApplication(ExtDocApplication):
    """
    ConfDBQuery application
    """

    title = "ConfDBQuery"
    menu = [_("Setup"), _("ConfDB Queries")]
    model = ConfDBQuery
    glyph = "file-code-o"

    def clean(self, data):
        data = super().clean(data)
        src = data.get("source", "")
        try:
            Engine().compile(src)
        except SyntaxError as e:
            raise ValueError("Syntax error: %s", e)
        return data
