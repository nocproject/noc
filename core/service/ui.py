# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UI backend service
##----------------------------------------------------------------------
## Copyright (C) 2007-1016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import hashlib
import logging
## Third-party modules
import tornado.web
import tornado.template
import tornado.httpserver
try:
    import jsmin
except ImportError:
    jsmin = None
# NOC modules
from base import Service

logger = logging.getLogger("ui")


class UIHandler(tornado.web.RequestHandler):
    hash = None
    PREFIX = os.getcwd()
    CACHE_ROOT = "var/ui/cache"
    CACHE_URL = "/ui/cache/"

    def initialize(self, name, *args, **kwargs):
        self.name = name

    def get(self):
        # @todo: Expose addiitonal context variables
        index_path = os.path.join(self.PREFIX, "ui",
                                  self.name, "index.html")
        return self.render(
            index_path,
            mergecache=self.mergecache,
            hashed=self.hashed
        )

    def mergecache(self, jslist):
        if self.hash is None:
            logger.debug("Calculating JS hash")
            r = []
            for path in jslist:
                p = path
                if p.startswith("/"):
                    p = p[1:]
                p = os.path.join(self.PREFIX, p)
                with open(p) as f:
                    r += [f.read()]
            js = "\n".join(r)
            if jsmin:
                ssize = len(js)
                js = jsmin.jsmin(js)
                logger.info("Minifying JS: %s -> %s", ssize, len(js))
            self.hash = hashlib.sha256(js).hexdigest()[:8]
            cache_path = os.path.join(self.CACHE_ROOT, "%s.js" % self.hash)
            if not os.path.isfile(cache_path):
                logger.info("Writing cached JS to %s", cache_path)
                with open(cache_path, "w") as f:
                    f.write(js)
        return "<script src=\"/ui/cache/%s.js\" " \
               "type=\"text/javascript\"></script>" % self.hash

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
        with open(path) as f:
            hash = hashlib.sha256(f.read()).hexdigest()[:8]
        return "%s?%s" % (url, hash)


class UIService(Service):
    def get_handlers(self):
        """
        Initialize additional application handlers
        """
        return super(UIService, self).get_handlers() + [
            (r"^/$", UIHandler, {
                "name": self.name
            })
        ]
