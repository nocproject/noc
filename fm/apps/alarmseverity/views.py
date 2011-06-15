# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm Severity
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
## NOC modules
from noc.lib.app import TreeApplication
from noc.fm.models import AlarmSeverity


class AlarmSeverityApplication(TreeApplication):
    title = _("Alarm Severities")
    verbose_name = _("Alarm Severity")
    verbose_name_plural = _("Alarm Severities")
    menu = "Setup | Alarm Severities"
    model = AlarmSeverity
