# ---------------------------------------------------------------------
# sa.actioncommands application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import jinja2

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.actioncommands import ActionCommands
from noc.core.translation import ugettext as _


class ActionCommandsApplication(ExtDocApplication):
    """
    ActionCommands application
    """

    title = _("Action Command")
    menu = [_("Setup"), _("Action Commands")]
    model = ActionCommands

    def clean(self, data):
        data = super().clean(data)
        try:
            jinja2.Template(data["commands"])
        except Exception as e:
            raise ValueError("Invalid template: %s", e)
        return data
