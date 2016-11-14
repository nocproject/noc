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
from noc.services.login.backends.base import BaseAuthBackend


class LoginService(UIService):
    name = "login"
    process_name = "noc-%(name).10s-%(instance).3s"
    api = [
        LoginAPI
    ]
    use_translation = True

    def get_handlers(self):
        return super(LoginService, self).get_handlers() + [
            ("^/api/auth/auth/$", AuthRequestHandler, {"service": self}),
            ("^/api/login/logout/$", LogoutRequestHandler)
        ]

    # Fields excluded from logging
    HIDDEN_FIELDS = [
        "password",
        "new_password",
        "old_password",
        "retype_password"
    ]

    def iter_methods(self):
        for m in self.config.method.split(","):
            yield m.strip()

    def authenticate(self, handler, credentials):
        """
        Authenticate user. Returns True when user is authenticated
        """
        c = credentials.copy()
        for f in self.HIDDEN_FIELDS:
            if f in c:
                c[f] = "***"
        le = "No active auth methods"
        for method in self.iter_methods():
            bc = BaseAuthBackend.get_backend(method)
            if not bc:
                self.logger.error("Cannot initialize backend '%s'", method)
                continue
            backend = bc(self)
            self.logger.info(
                "Authenticating credentials %s using method %s",
                c, method
            )
            try:
                backend.authenticate(**credentials)
            except backend.LoginError as e:
                le = str(e)
                continue
            self.logger.info("Authorized credentials: %s", c)
            # Set cookie
            handler.set_secure_cookie(
                "noc_user",
                credentials.get("user"),
                expires_days=self.config.session_ttl
            )
            return True
        self.logger.error("Login failed for %s: %s", c, le)
        return False

    def change_credentials(self, handler, credentials):
        """
        Change credentials. Return true when credentials changed
        """
        c = credentials.copy()
        for f in self.HIDDEN_FIELDS:
            if f in c:
                c[f] = "***"
        r = False
        for method in self.iter_methods():
            bc = BaseAuthBackend.get_backend(method)
            if not bc:
                self.logger.error("Cannot initialize backend '%s'", method)
                continue
            backend = bc(self)
            self.logger.info("Changing credentials %s using method %s",
                             c, method)
            try:
                backend.change_credentials(**credentials)
                r = True
            except NotImplementedError:
                continue
            except backend.LoginError as e:
                self.logger.error(
                    "Failed to change credentials for %s: %s", c, e
                )
            self.logger.info("Changed user credentials: %s", c)
        return r

if __name__ == "__main__":
    LoginService().start()
