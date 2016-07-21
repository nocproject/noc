# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.welcome application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _


class WelcomeApplication(ExtApplication):
    """
    main.welcome application
    """
    title = _("Welcome")
