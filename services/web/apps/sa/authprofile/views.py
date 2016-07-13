# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.authprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models.authprofile import AuthProfile
from noc.core.translation import ugettext as _


class AuthProfileApplication(ExtModelApplication):
    """
    AuthProfile application
    """
    title = _("Auth Profile")
    menu = [_("Setup"), _("Auth Profiles")]
    model = AuthProfile
