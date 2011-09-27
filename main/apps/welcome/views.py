# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.welcome application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view, PermitLogged


class WelcomeAppplication(ExtApplication):
    """
    main.welcome application
    """
    title = "Welcome"

    @view(method=["GET"], url=r"^$", access=PermitLogged(), api=True)
    def api_welcome(self, request):
        return self.render_template("welcome.html")
