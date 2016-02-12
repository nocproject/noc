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


class LoginService(UIService):
    name = "login"


if __name__ == "__main__":
    LoginService().start()
