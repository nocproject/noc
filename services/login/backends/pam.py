# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PAM Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pam
# NOC modules
from base import BaseAuthBackend


class PAMBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        pam = pam.pam()
        r = pam.authenticate(user, password,
                             service=self.service.config.pam_service)
        if not r:
            raise self.LoginError("PAM authentication failed")
        return user
