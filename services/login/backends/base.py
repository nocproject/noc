# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Authentication Backends
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


class BaseAuthBackend(object):
    class LoginError(Exception):
        pass

    def __init__(self, service):
        self.service = service
        self.logger = logging.getLogger("auth")

    def authenticate(self, **kwargs):
        """
        Authenticate user using given credentials.
        Raise LoginError when failed
        """
        raise self.LoginError()

    def change_credentials(self, **kwargs):
        """
        Change credentials.
        Raise LoginError when failed
        """
        raise self.LoginError(
            "Cannot change credentials with selected method"
        )

    def ensure_user(self, username, is_active=True, **kwargs):
        from django.contrib.auth.models import User
        changed = False
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            self.logger.info("Creating local user %s", username)
            u = User(
                username=username,
                is_active=is_active
            )
            changed = True
        for k, v in [("is_active", is_active)]:
            cv = getattr(u, k)
            if cv != v:
                self.logger.info(
                    "Changing user %s %s: %s -> %s",
                    username, k, cv, v
                )
                setattr(u, k, v)
                changed = True
        # Check changes
        if changed:
            u.save()

    def _user_in_group(self, user, group):
        return user.groups.filter(id=group.id).exists()

    def ensure_group(self, user, group):
        if not self._user_in_group(user, group):
            self.logger.info("Adding user %s to group %s",
                             user.username, group.name)
            user.groups.add(group)

    def deny_group(self, user, group):
        if self._user_in_group(user, group):
            self.logger.info("Removing user %s from group %s",
                             user.username, group.groupname)
            user.groups.remove(group)
