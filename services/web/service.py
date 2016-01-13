#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Web service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
import tornado.web
import tornado.httpserver
import tornado.web
import tornado.wsgi
import django.core.handlers.wsgi
## NOC modules
from noc.core.service.base import Service


class WebService(Service):
    name = "web"
    api = []

    def __init__(self):
        super(WebService, self).__init__()

    def on_activate(self):
        prefix = os.getcwd()
        # NOC WSGI handler
        noc_wsgi = tornado.wsgi.WSGIContainer(
                django.core.handlers.wsgi.WSGIHandler()
        )

        addr, port = self.get_service_address()
        self.logger.info("Running HTTP server at http://%s:%s/",
                         addr, port)
        app = tornado.web.Application([
            # /static/
            (r"^/static/(.*)", tornado.web.StaticFileHandler, {
                "path": "static"}),
            # /media/
            (r"^/media/(.*)", tornado.web.StaticFileHandler, {
                "path": "lib/python/site-packages/django/contrib/admin/static"
            }),
            # NOC application's js, img and css files
            # @todo: write proper static handler
            (
            r"(/[^/]+/[^/]+/(?:js|img|css)/.+)", AppStaticFileHandler, {
                "path": prefix}),
            # / -> /main/desktop/
            (r"^/$", tornado.web.RedirectHandler, {
                "url": "/main/desktop/"}),
            # Serve mercurial repo
            (r"^/hg/static/(.*)", tornado.web.StaticFileHandler, {
                "path": "lib/python/site-packages/mercurial/templates/static"
            }),
            # Pass to NOC
            (r"^.*$", AppHandler, {"fallback": noc_wsgi})
        ])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port, addr)
        # Initialize site
        self.logger.info("Registering web applications")
        from noc.lib.app import site
        site.autodiscover()


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


class AppHandler(tornado.web.FallbackHandler):
    def prepare(self):
        if self.request.path == "/render":
            # Rewrite /render -> /pm/render/
            self.request.path = "/pm/render/"
            self.request.uri = "/pm/render/" + self.request.uri[7:]
        elif self.request.path == "/metrics/find/":
            # Rewrite /metrics/find -> /pm/metric/find/
            self.request.path = "/pm/metric/find/"
            self.request.uri = "/pm/metric/find/" + self.request.uri[
                                                    14:]
        super(AppHandler, self).prepare()


if __name__ == "__main__":
    WebService().start()
