# ---------------------------------------------------------------------
# PAM Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pam

# NOC modules
from noc.config import config
from .base import BaseAuthBackend


class PAMBackend(BaseAuthBackend):
    def authenticate(self, user: str = None, password: str = None, **kwargs) -> str:
        p = pam.pam()
        r = p.authenticate(user, password, service=config.login.pam_service)
        if not r:
            raise self.LoginError("PAM authentication failed")
        return user
