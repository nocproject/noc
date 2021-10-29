# ---------------------------------------------------------------------
# fm.alarmgrouprule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.fm.models.alarmgrouprule import AlarmGroupRule
from noc.core.translation import ugettext as _


class AlarmGroupRuleApplication(ExtDocApplication):
    """
    AlarmGroup application
    """

    title = "Alarm Group Rules"
    menu = [_("Setup"), _("Alarm Group Rules")]
    model = AlarmGroupRule
