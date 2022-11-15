# ---------------------------------------------------------------------
# fm.alarmtrigger application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.fm.models.alarmtrigger import AlarmTrigger
from noc.core.translation import ugettext as _


class AlarmTriggerApplication(ExtModelApplication):
    """
    AlarmTrigger application
    """

    title = _("Alarm Triggers")
    menu = [_("Setup"), _("Alarm Triggers")]
    model = AlarmTrigger
