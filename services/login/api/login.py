# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Login API
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
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
        credentials["ip"] = self.request.remote_ip
        if self.service.authenticate(self.handler, credentials):
            return True
        else:
            return False

    @api
    def change_credentials(self, credentials):
        """
        Change credentials
        """
        if self.service.change_credentials(
            self.handler,
            credentials
        ):
            return True
        else:
            return False
