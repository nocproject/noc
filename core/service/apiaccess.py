# ----------------------------------------------------------------------
# APIAccessRequestHandler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import functools
import urllib.parse

# Third-party modules
import tornado.web


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)

    return wrapper


class APIAccessRequestHandler(tornado.web.RequestHandler):
    """
    Check X-NOC-API-Access header
    """

    # Set of allowed access tokens
    # Access tokens are <api>:<role> or <api>:* for wildcard
    access_tokens_set = set()
    API_ACCESS_HEADER = "X-NOC-API-Access"

    def get_access_tokens_set(self):
        return self.access_tokens_set

    def get_current_user(self):
        api_access = urllib.parse.unquote(self.request.headers.get(self.API_ACCESS_HEADER, ""))
        a_set = set(api_access.split(","))
        if self.get_access_tokens_set() & a_set:
            return True
        return None
