# ---------------------------------------------------------------------
# fm.alarmrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.fm.models.alarmrule import AlarmRule
from noc.core.translation import ugettext as _


class AlarmRuleApplication(ExtDocApplication):
    """
    AlarmGroup application
    """

    title = "Alarm Rules"
    menu = [_("Setup"), _("Alarm Rules")]
    model = AlarmRule
