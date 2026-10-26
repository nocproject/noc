# ----------------------------------------------------------------------
# inv.techdomain application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.techdomain import TechDomain
from noc.services.web.base.extdocapplication import ExtDocApplication


class TechDomainApplication(ExtDocApplication):
    """
    TechDomain application
    """

    title = _("Tech Domain")
    menu = [_("Setup"), _("Tech Domains")]
    model = TechDomain
    glyph = "flask"
