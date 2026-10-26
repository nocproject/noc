# ---------------------------------------------------------------------
# fm.alarmescalation application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.services.web.base.extdocapplication import ExtDocApplication


class AlarmEscalationApplication(ExtDocApplication):
    """
    AlarmEscalation application
    """

    title = _("Alarm Escalation")
    menu = [_("Setup"), _("Alarm Escalation")]
    model = AlarmEscalation
