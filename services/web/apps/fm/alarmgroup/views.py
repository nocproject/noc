# ---------------------------------------------------------------------
# fm.alarmgroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.fm.models.alarmgroup import AlarmGroup
from noc.core.translation import ugettext as _


class AlarmGroupApplication(ExtDocApplication):
    """
    AlarmGroup application
    """

    title = "Alarm Group Config"
    menu = [_("Setup"), _("Alarm Group")]
    model = AlarmGroup
