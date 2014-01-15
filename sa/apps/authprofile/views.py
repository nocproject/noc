# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.authprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import AuthProfile


class AuthProfileApplication(ExtModelApplication):
    """
    AuthProfile application
    """
    title = "Auth Profile"
    menu = "Setup | Auth Profiles"
    model = AuthProfile
