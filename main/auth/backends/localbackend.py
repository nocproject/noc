# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Local Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import NOCAuthBackend


class NOCLocalBackend(NOCAuthBackend):
    """
    Local authentication against auth_user database table.
    """
    can_change_credentials = True

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = self.User.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.User.DoesNotExist:
            pass
        return None

    def change_credentials(self, user, old_password,
                           new_password, retype_password, **kwargs):
        if not user.check_password(old_password):
            raise ValueError("Invalid password")
        if new_password != retype_password:
            raise ValueError("Passwords not match")
        user.set_password(new_password)
        user.save()
