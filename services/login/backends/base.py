# ---------------------------------------------------------------------
# Authentication Backends
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

logger = logging.getLogger(__name__)


class BaseAuthBackend(object):
    class LoginError(Exception):
        pass

    _methods = {}

    def __init__(self):
        self.logger = logger

    def authenticate(self, **kwargs):
        """
        Authenticate user using given credentials.
        Raise LoginError when failed

        :return: User name
        :raises LoginError: Authentication error
        """
        raise self.LoginError()

    def change_credentials(self, **kwargs):
        """
        Change credentials.
        Raise LoginError when failed
        """
        raise NotImplementedError

    def ensure_user(
        self, username, is_active=True, first_name=None, last_name=None, email=None, **kwargs
    ):
        from noc.aaa.models.user import User

        changed = False
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            self.logger.info("Creating local user %s", username)
            u = User(username=username, is_active=is_active)
            u.set_unusable_password()
            changed = True
        for k, v in [
            ("is_active", is_active),
            ("first_name", first_name),
            ("last_name", last_name),
            ("email", email),
        ]:
            cv = getattr(u, k)
            if cv != v and v is not None:
                self.logger.info("Changing user %s %s: %s -> %s", username, k, cv, v)
                setattr(u, k, v)
                changed = True
        # Check changes
        if changed:
            u.save()
        return u

    def _user_in_group(self, user, group):
        return user.groups.filter(id=group.id).exists()

    def ensure_group(self, user, group):
        if not self._user_in_group(user, group):
            self.logger.info("Adding user %s to group %s", user.username, group.name)
            user.groups.add(group)

    def deny_group(self, user, group):
        if self._user_in_group(user, group):
            self.logger.info("Removing user %s from group %s", user.username, group.name)
            user.groups.remove(group)
