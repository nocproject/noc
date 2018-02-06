# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RemoteUser Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User
import cachetools
# NOC modules
from noc.core.perf import metrics
from noc.core.debug import ErrorReport

user_lock = Lock()


class RemoteUserMiddleware(object):
    """
    Authenticate against REMOTE_USER request header

    Middleware for utilizing Web-server-provided authentication.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``REMOTE_USER`` request header.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    The header used is configurable and defaults to ``REMOTE_USER``.  Subclass
    this class and change the ``header`` attribute if you need to use a
    different header.
    """
    HEADER = "HTTP_REMOTE_USER"

    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def process_request(self, request):
        # Get username from REMOTE_USER
        user_name = request.META.get(self.HEADER)
        if user_name:
            request.user = SimpleLazyObject(lambda: self.get_user_by_name(user_name))
        else:
            request.user = None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_user_cache"), lock=lambda _: user_lock)
    def get_user_by_name(cls, name):
        with ErrorReport():
            user = User.objects.filter(username=name)[:1]
            if user:
                return user[0]
            else:
                metrics["error", ("type", "user_not_found")] += 1
                return None

    def get_user(self, user_name):
        return self.get_user_by_name(user_name)
