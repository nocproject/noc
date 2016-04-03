# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Local Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseAuthBackend
from noc.main.models import User


class LocalBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise self.LoginError("User does not exists")
        if not user.check_password(password):
            raise self.LoginError("Invalid password")
