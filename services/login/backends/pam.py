# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PAM Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import pam
# NOC modules
from noc.config import config
from .base import BaseAuthBackend


class PAMBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        p = pam.pam()
        r = p.authenticate(user, password,
                           service=config.login.pam_service)
        if not r:
            raise self.LoginError("PAM authentication failed")
        return user
