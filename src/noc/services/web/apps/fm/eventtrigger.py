# ---------------------------------------------------------------------
# fm.eventtrigger application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.fm.models.eventtrigger import EventTrigger
from noc.services.web.base.extmodelapplication import ExtModelApplication


class EventTriggerApplication(ExtModelApplication):
    """
    EventTrigger application
    """

    title = _("Event Triggers")
    menu = [_("Setup"), _("Event Triggers")]
    model = EventTrigger
