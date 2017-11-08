# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.actioncommands application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.template import Template
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sa.models.actioncommands import ActionCommands


class ActionCommandsApplication(ExtDocApplication):
    """
    ActionCommands application
    """
    title = _("Action Command")
    menu = [_("Setup"), _("Action Commands")]
    model = ActionCommands

    def clean(self, data):
        data = super(ActionCommandsApplication, self).clean(data)
        try:
            Template(data["commands"])
        except Exception as e:
            raise ValueError("Invalid template: %s", e)
        return data
