# ---------------------------------------------------------------------
# fm.eventcategory application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.eventcategory import EventCategory
from noc.core.translation import ugettext as _


class EscalationProfileApplication(ExtDocApplication):
    """
    EscalationProfile application
    """

    title = _("Event Category")
    menu = [_("Setup"), _("Event Categories")]
    model = EventCategory
