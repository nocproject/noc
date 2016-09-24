# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parallel command execution
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extapplication import ExtApplication
from noc.core.translation import ugettext as _


class RunCommandsApplication(ExtApplication):
    title = _("Run Commands")
    menu = [_("Run Commands")]

    implied_permissions = {
        "launch": [
            "sa:objectlist:read"
        ]
    }
