# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.welcome application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
# Third-party modules
from jinja2 import Template
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _


class WelcomeApplication(ExtApplication):
    """
    main.welcome application
    """
    title = _("Welcome")
    WELCOME_PATH = [
        "custom/services/web/apps/main/welcome/templates/Welcome.html.j2",
        "services/web/apps/main/welcome/templates/Welcome.html.j2",
    ]

    @view(url="^welcome/$", access=True, api=True)
    def api_welcome(self, request):
        setup = {"installation_name": self.config.get("customization", "installation_name")}
        for p in self.WELCOME_PATH:
            if not os.path.exists(p):
                continue
            with open(p) as f:
                tpl = Template(f.read())
            return self.render_response(tpl.render(setup=setup), "text/html")  # @todo: Fill context
        return "You are not welcome!"
