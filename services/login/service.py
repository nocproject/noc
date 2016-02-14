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
from api.login import LoginAPI


class LoginService(UIService):
    name = "login"
    api = [
        LoginAPI
    ]

    def get_handlers(self):
        return super(LoginService, self).get_handlers() + [
            ("^/auth/$", AuthRequestHandler)
        ]


if __name__ == "__main__":
    LoginService().start()
