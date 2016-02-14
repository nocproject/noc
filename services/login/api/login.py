# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Login API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.api import API, APIError, api


class LoginAPI(API):
    """
    Login API
    """
    name = "login"

    @api
    def login(self, credentials):
        """
        Authenticate user
        """
        self.handler.set_secure_cookie(
            "noc_user",
            credentials.get("user")
        )
        return True
