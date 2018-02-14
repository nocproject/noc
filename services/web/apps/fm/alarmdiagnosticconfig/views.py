# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.alarmdiagnosticconfig application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.fm.models.alarmdiagnosticconfig import AlarmDiagnosticConfig
from noc.core.translation import ugettext as _


class AlarmDiagnosticConfigApplication(ExtDocApplication):
    """
    AlarmDiagnosticConfig application
    """
    title = "Alarm Diagnostic Config"
    menu = [_("Setup"), _("Alarm Diagnostic")]
    model = AlarmDiagnosticConfig
