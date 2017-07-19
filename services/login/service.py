#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Login service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.ui import UIService
from noc.services.login.auth import AuthRequestHandler
from noc.services.login.logout import LogoutRequestHandler
from noc.services.login.api.login import LoginAPI
from noc.services.login.backends.base import BaseAuthBackend
from noc.config import config


class LoginService(UIService):
    name = "login"
    process_name = "noc-%(name).10s-%(instance).2s"
    api = [
        LoginAPI
    ]
    use_translation = True
    traefik_backend = "login"
    traefik_frontend_rule = "PathPrefix:/api/login,/api/auth/auth"

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
        for m in config.login.methods.split(","):
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
                user = backend.authenticate(**credentials)
            except backend.LoginError as e:
                self.logger.info("[%s] Login Error: %s", method, e)
                le = str(e)
                continue
            self.logger.info("Authorized credentials %s as user %s", c, user)
            # Set cookie
            handler.set_secure_cookie(
                "noc_user",
                user,
                expires_days=config.login.session_ttl
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
