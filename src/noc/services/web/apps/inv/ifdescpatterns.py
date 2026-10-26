# ----------------------------------------------------------------------
# inv.ifdescpatterns application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.ifdescpatterns import IfDescPatterns
from noc.services.web.base.extdocapplication import ExtDocApplication


class IfDescPatternsApplication(ExtDocApplication):
    """
    IfDescPatterns application
    """

    title = "IfDesc Patterns"
    menu = [_("Setup"), _("IfDesc Patterns")]
    model = IfDescPatterns
