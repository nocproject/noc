# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Login API
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.api import API, APIError, api
from noc.lib.solutions import get_solution


class LoginAPI(API):
    """
    Login API
    """
    name = "login"

    # Fields excluded from logging
    HIDDEN_FIELDS = [
        "password"
    ]

    @api
    def login(self, credentials):
        """
        Authenticate user
        """
        method = self.service.config.method
        try:
            backend = get_solution(method)(self.service)
        except Exception as e:
            self.logger.error(
                "Failed to initialize '%s' backend: %s",
                method, e
            )
            return False
        credentials["ip"] = self.request.remote_ip
        c = credentials.copy()
        for f in self.HIDDEN_FIELDS:
            if f in c:
                c[f] = "***"
        self.logger.info("Authenticating credentials %s using method",
                         c, method)
        try:
            backend.authenticate(**credentials)
        except backend.LoginError as e:
            self.logger.error("Login failed for %s: %s", c, e)
            return False
        self.handler.set_secure_cookie(
            "noc_user",
            credentials.get("user"),
            expires_days=self.service.config.session_ttl
        )
        return True
