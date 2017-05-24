# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.alarmseverity application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.core.translation import ugettext as _


class AlarmSeverityApplication(ExtDocApplication):
    """
    AlarmSeverity application
    """
    title = _("Alarm Severity")
    menu = [_("Setup"), _("Alarm Severities")]
    model = AlarmSeverity

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
