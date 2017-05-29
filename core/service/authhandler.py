# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Authenticated Request Handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
import cachetools
import tornado.web
# NOC modules
from noc.main.models import User

user_lock = Lock()


class AuthRequestHandler(tornado.web.RequestHandler):
    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def initialize(self, service=None):
        self.service = service

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_user_cache"),
                             lock=lambda _: user_lock)
    def get_user_by_name(cls, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            return None

    def get_current_user(self):
        return self.get_user_by_name(
            self.request.headers.get("Remote-User")
        )
