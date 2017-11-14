# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Authentication Backends
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import logging
from threading import Lock
import operator
import inspect
# Third-party modules
import cachetools
from noc.config import config

id_lock = Lock()


class BaseAuthBackend(object):
    class LoginError(Exception):
        pass

    _methods = {}

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
        raise NotImplementedError

    def ensure_user(self, username, is_active=True,
                    first_name=None, last_name=None, email=None,
                    **kwargs):
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
            u.set_unusable_password()
            changed = True
        for k, v in [
            ("is_active", is_active),
            ("first_name", first_name),
            ("last_name", last_name),
            ("email", email)
        ]:
            cv = getattr(u, k)
            if cv != v and v is not None:
                self.logger.info(
                    "Changing user %s %s: %s -> %s",
                    username, k, cv, v
                )
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
            self.logger.info("Adding user %s to group %s",
                             user.username, group.name)
            user.groups.add(group)

    def deny_group(self, user, group):
        if self._user_in_group(user, group):
            self.logger.info("Removing user %s from group %s",
                             user.username, group.name)
            user.groups.remove(group)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_methods"), lock=lambda _: id_lock)
    def get_backend(cls, name):
        """
        Look for custom auth methods in custom and load it.
        First check if custom method with same name exists then use bundled one.
        :param name: param name
        :return: found auth method
        """
        import logging
        logger = logging.getLogger(__name__)
        m = None
        custom_path = os.path.join(config.path.custom_path, "services/login/backends")
        for mm in [
            "%s/%s.py" % (custom_path, name),
            "services/login/backends.%s.py" % name
        ]:
            if not os.path.exists(mm):
                continue
            if mm.startswith(".."):
                mm = mm.replace(config.path.custom_path, "")[1:]
            mn = "%s.%s" % (
                os.path.basename(config.path.custom_path),
                mm.replace("/", ".")[:-3]
            )
            try:
                m = __import__(mn, {}, {}, "*")
                logger.debug("Successfuly imported %s", m)
            except ImportError as e:
                logger.debug("There was an error importing %s with %s %s", e, m, mn)
                pass
        if m is None:
            return None
        for a in dir(m):
            o = getattr(m, a)
            if (
                inspect.isclass(o) and
                issubclass(o, BaseAuthBackend) and
                o.__module__ == m.__name__
            ):
                return o
        return None
