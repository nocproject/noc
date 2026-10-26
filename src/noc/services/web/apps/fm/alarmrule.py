# ---------------------------------------------------------------------
# fm.alarmrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.fm.models.alarmrule import AlarmRule
from noc.services.web.base.extdocapplication import ExtDocApplication


class AlarmRuleApplication(ExtDocApplication):
    """
    AlarmGroup application
    """

    title = "Alarm Rules"
    menu = [_("Setup"), _("Alarm Rules")]
    model = AlarmRule
