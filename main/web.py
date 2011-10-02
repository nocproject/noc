# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-web daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
import django.core.handlers.wsgi
## Third-party modules
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.httpserver
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.debug import error_report


class AppStaticFileHandler(tornado.web.StaticFileHandler):
    """
    Serve applications' static files.
    Rewrite urls from
    /<module>/<app>/(js|img|css)/file
    to
    <module>/apps/<app>/(js|img|css)/file
    """
    def get(self, path, include_body=True):
        p = path.split("/")
        path = "/".join([p[1], "apps"] + p[2:])
        return super(AppStaticFileHandler, self).get(path, include_body)


class Web(Daemon):
    """
    noc-web daemon
    """
    daemon_name = "noc-web"

    def setup_opt_parser(self):
        """
        Add --listen option
        """
        self.opt_parser.add_option("-l", "--listen", action="store",
                                   dest="listen", default="",
                                   help="listen at address:port")

    def run(self):
        if self.options.listen:
            listen = self.options.listen
        else:
            listen = self.config.get("web", "listen")
        if ":" in listen:
            address, port = listen.split(":")
        else:
            address, port = "127.0.0.1", listen
        port = int(port)

        noc_wsgi = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler()
        )

        application = tornado.web.Application([
            # /static/
            (r"^/static/(.*)", tornado.web.StaticFileHandler, {
                "path": "static"}),
            # /media/
            (r"^/media/(.*)", tornado.web.StaticFileHandler, {
                "path": "contrib/lib/django/contrib/admin/media"}),
            # /doc/
            (r"^/doc/(.*)", tornado.web.StaticFileHandler, {
                "path": "share/doc/users_guide/html"}),
            # NOC application's js, img and css files
            # @todo: write proper static handler
            (r"(/[^/]+/[^/]+/(?:js|img|css)/.+)", AppStaticFileHandler, {
                "path": self.prefix}),
            # / -> /main/desktop/
            (r"^/$", tornado.web.RedirectHandler, {"url": "/main/desktop/"}),
            # Pass to NOC
            (r"^.*$", tornado.web.FallbackHandler, {"fallback": noc_wsgi})
        ])
        logging.info("Loading site")
        # Import and autodiscover site
        # Called within function to prevent import loops
        import noc.lib.nosql  # Connect to mongodb
        from noc.lib.app import site
        site.autodiscover()
        logging.info("Listening %s:%s" % (address, port))
        server = tornado.httpserver.HTTPServer(application)
        server.bind(port, address)
        # Fork multiple instances
        server.start(self.config.getint("web", "workers"))
        tornado.ioloop.IOLoop.instance().start()
