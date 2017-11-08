# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.alarmclassconfig application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.fm.models.alarmclassconfig import AlarmClassConfig
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class AlarmClassConfigApplication(ExtDocApplication):
    """
    AlarmClassConfig application
    """
    title = _("Alarm Class Config")
    menu = [_("Setup"), _("Alarm Class Config")]
    model = AlarmClassConfig
