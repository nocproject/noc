# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.ignoreeventrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.fm.models.ignoreeventrules import IgnoreEventRules
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.sa.interfaces.base import REParameter


class IgnoreEventRuleApplication(ExtModelApplication):
    """
    IgnoreEventRule application
    """
    title = _("Ignore Event Rules")
    menu = [_("Setup"), _("Ignore Event Rules")]
    model = IgnoreEventRules

    clean_fields = {
        "left_re": REParameter(),
        "right_re": REParameter()
    }
