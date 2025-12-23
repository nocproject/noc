# ---------------------------------------------------------------------
# fm.alarmseverity application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.core.translation import ugettext as _


class AlarmSeverityApplication(ExtDocApplication):
    """
    AlarmSeverity application
    """

    title = _("Alarm Severity")
    menu = [_("Setup"), _("Alarm Severities")]
    model = AlarmSeverity
