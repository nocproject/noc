# ----------------------------------------------------------------------
# main.label application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.label import Label
from noc.core.translation import ugettext as _


class LabelApplication(ExtDocApplication):
    """
    Label application
    """

    title = "Label"
    menu = [_("Setup"), _("Labels")]
    glyph = "tag"
    model = Label
    query_condition = "icontains"
