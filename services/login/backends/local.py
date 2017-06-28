# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Local Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from base import BaseAuthBackend
from noc.main.models import User
from noc.core.translation import ugettext as _


class LocalBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise self.LoginError(_("User does not exists"))
        if not user.check_password(password):
            raise self.LoginError(_("Invalid password"))
        return user.username

    def change_credentials(self, user=None, old_password=None,
                           new_password=None, **kwargs):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise self.LoginError(_("User does not exists"))
        if not user.check_password(old_password):
            raise self.LoginError(_("Invalid password"))
        user.set_password(new_password)
        user.save()
