# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# UI backend service
# ----------------------------------------------------------------------
# Copyright (C) 2007-1017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import hashlib
import logging
# Third-party modules
import tornado.web
# NOC modules
from .base import Service

logger = logging.getLogger("ui")


class UIHandler(tornado.web.RequestHandler):
    hash = None
    PREFIX = os.getcwd()

    def initialize(self, service, *args, **kwargs):
        self.service = service
        self.name = self.service.name

    def get(self):
        index_path = os.path.join(self.PREFIX, "ui",
                                  self.name, "index.html")
        self.set_header("Cache-Control", "no-cache; must-revalidate")
        self.set_header("Expires", "0")
        language = self.service.config.language
        return self.render(
            index_path,
            hashed=self.hashed,
            request=self.request,
            language=language,
            name=self.name,
            service=self.service
        )

    def hashed(self, url):
        """
        Convert path to path?hash version
        :param path:
        :return:
        """
        u = url
        if u.startswith("/"):
            u = url[1:]
        path = os.path.join(self.PREFIX, u)
        if not os.path.exists(path):
            return "%s?%s" % (url, "00000000")
        with open(path) as f:
            hash = hashlib.sha256(f.read()).hexdigest()[:8]
        return "%s?%s" % (url, hash)


class UIService(Service):
    def get_handlers(self):
        """
        Initialize additional application handlers
        """
        return super(UIService, self).get_handlers() + [
            (r"^/api/%s/index.html$" % self.name, UIHandler, {
                "service": self
            })
        ]
