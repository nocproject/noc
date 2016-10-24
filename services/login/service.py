#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Login service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.ui import UIService
from auth import AuthRequestHandler
from logout import LogoutRequestHandler
from api.login import LoginAPI
from noc.core.handler import get_handler


class LoginService(UIService):
    name = "login"
    process_name = "noc-%(name).10s-%(instance).3s"
    api = [
        LoginAPI
    ]
    use_translation = True

    def get_handlers(self):
        return super(LoginService, self).get_handlers() + [
            ("^/auth/$", AuthRequestHandler, {"service": self}),
            ("^/logout/$", LogoutRequestHandler)
        ]

    # Fields excluded from logging
    HIDDEN_FIELDS = [
        "password",
        "new_password",
        "old_password",
        "retype_password"
    ]

    def authenticate(self, handler, credentials):
        """
        Authenticate user. Returns True when user is authenticated
        """
        method = self.config.method
        try:
            backend = get_handler(method)(self)
        except Exception as e:
            self.logger.error(
                "Failed to initialize '%s' backend: %s",
                method, e
            )
            return False
        c = credentials.copy()
        for f in self.HIDDEN_FIELDS:
            if f in c:
                c[f] = "***"
        self.logger.info("Authenticating credentials %s using method %s",
                         c, method)
        try:
            backend.authenticate(**credentials)
        except backend.LoginError as e:
            self.logger.error("Login failed for %s: %s", c, e)
            return False
        self.logger.info("Authorized")
        # Set cookie
        handler.set_secure_cookie(
            "noc_user",
            credentials.get("user"),
            expires_days=self.config.session_ttl
        )
        return True

    def change_credentials(self, handler, credentials):
        """
        Change credentials. Return true when credentials changed
        """
        method = self.config.method
        try:
            backend = get_handler(method)(self)
        except Exception as e:
            self.logger.error(
                "Failed to initialize '%s' backend: %s",
                method, e
            )
            return False
        c = credentials.copy()
        for f in self.HIDDEN_FIELDS:
            if f in c:
                c[f] = "***"
        self.logger.info("Changing credentials %s using method %s",
                         c, method)
        try:
            backend.change_credentials(**credentials)
        except backend.LoginError as e:
            self.logger.error(
                "Failed to change credentials for %s: %s", c, e
            )
            return False
        self.logger.info("Changed")
        return True

if __name__ == "__main__":
    LoginService().start()
