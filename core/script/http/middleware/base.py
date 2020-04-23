# ----------------------------------------------------------------------
# BaseMiddleware class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseMiddleware(object):
    name = None

    def __init__(self, http):
        self.http = http

    def process_request(self, url, body, headers):
        return url, body, headers

    def process_get(self, url, body, headers):
        return self.process_request(url, body, headers)

    def process_post(self, url, body, headers):
        return self.process_request(url, body, headers)

    def process_put(self, url, body, headers):
        return self.process_request(url, body, headers)
