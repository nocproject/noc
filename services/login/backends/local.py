# ---------------------------------------------------------------------
# Local Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.aaa.models.user import User
from noc.core.translation import ugettext as _
from .base import BaseAuthBackend


class LocalBackend(BaseAuthBackend):
    def authenticate(self, user: str = None, password: str = None, **kwargs) -> str:
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise self.LoginError(_("User does not exists"))
        if not user.check_password(password):
            raise self.LoginError(_("Invalid password"))
        if not user.can_login_now():
            raise self.LoginError(_("User account is blocked"))
        return user.username

    def change_credentials(self, user=None, old_password=None, new_password=None, **kwargs):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise self.LoginError(_("User does not exists"))
        if not user.check_password(old_password):
            raise self.LoginError(_("Invalid password"))
        try:
            user.set_password(new_password)
        except ValueError as e:
            raise self.LoginError(str(e.args[0]))
