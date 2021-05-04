# ----------------------------------------------------------------------
# main.regexplabel application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.regexplabel import RegexpLabel
from noc.core.translation import ugettext as _


class RegexpLabelApplication(ExtDocApplication):
    """
    RegexpLabel application
    """

    title = _("Regexp Label")
    menu = [_("Setup"), _("Regexp Label")]
    model = RegexpLabel
    query_condition = "contains"
