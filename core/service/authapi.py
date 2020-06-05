# ----------------------------------------------------------------------
# Authenticated API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
import urllib.parse

# Third-party modules
import cachetools

# NOC modules
from .api import APIRequestHandler
from noc.aaa.models.user import User

user_lock = Lock()


class AuthAPIRequestHandler(APIRequestHandler):
    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_user_cache"), lock=lambda _: user_lock)
    def get_user_by_name(cls, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            return None

    def get_current_user(self):
        return self.get_user_by_name(
            urllib.parse.unquote(self.request.headers.get("Remote-User"))
        )
