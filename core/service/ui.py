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
    CACHE_ROOT = "var/ui/cache"
    CACHE_URL = "/ui/cache/"

    def initialize(self, path, *args, **kwargs):
        self.root = path

    def get(self):
        # @todo: Expose addiitonal context variables
        return self.render(
            os.path.join(self.root, "index.html"),
            mergecache=self.mergecache,
            hashed=self.hashed
        )

    def mergecache(self, jslist):
        if self.hash is None:
            logger.debug("Calculating JS hash")
            r = []
            for f in jslist:
                path = os.path.join(self.root, f)
                if os.path.isfile(path):
                    with open(path) as f:
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

    def hashed(self, path):
        """
        Convert path to path?hash version
        :param path:
        :return:
        """
        fp = path
        if fp.startswith("/ui/"):
            fp = fp[4:]
        fp = os.path.join(self.root, fp)
        with open(fp) as f:
            hash = hashlib.sha256(f.read()).hexdigest()[:8]
        return "%s?%s" % (path, hash)


class UIService(Service):
    def on_activate(self):
        addr, port = self.get_service_address()
        self.logger.info("Running HTTP server at http://%s:%s/",
                         addr, port)
        app = tornado.web.Application([
            (r"^.*$", UIHandler, {
                "index": "ui/login/"
            })
        ])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port, addr)
