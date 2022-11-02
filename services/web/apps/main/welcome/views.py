# ---------------------------------------------------------------------
# main.welcome application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os

# Third-party modules
from jinja2 import Template

# NOC modules
from noc.config import config
from noc.services.web.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _


class WelcomeApplication(ExtApplication):
    """
    main.welcome application
    """

    title = _("Welcome")
    WELCOME_PATH = config.get_customized_paths(
        os.path.join("services", "web", "apps", "main", "welcome", "templates", "Welcome.html.j2"),
        prefer_custom=True,
    )

    @view(url="^welcome/$", access=True, api=True)
    def api_welcome(self, request):
        setup = {"installation_name": config.installation_name}
        for p in self.WELCOME_PATH:
            if not os.path.exists(p):
                continue
            with open(p) as f:
                tpl = Template(f.read())
            return self.render_response(tpl.render(setup=setup), "text/html")  # @todo: Fill context
        return "You are not welcome!"
