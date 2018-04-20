# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-web daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import os
import sys
import errno
import signal
import socket
import time
## Django modules
import django.core.handlers.wsgi
## Third-party modules
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.httpserver
from tornado.process import cpu_count
import mercurial.ui
from mercurial.hgweb.hgwebdir_mod import hgwebdir
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.version import get_version
from noc.lib.perf import MetricsHub, run_reporter


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
            self.request.uri = "/pm/metric/find/" + self.request.uri[14:]
        super(AppHandler, self).prepare()


class HGHandler(tornado.web.FallbackHandler):
    def prepare(self):
        # Rewrite /hg -> /
        self.request.path = self.request.path[3:]
        super(HGHandler, self).prepare()


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

        # NOC WSGI handler
        noc_wsgi = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler()
        )

        # Mercurial handler
        ui = mercurial.ui.ui()
        ui.setconfig('ui', 'report_untrusted', 'off', 'hgwebdir')
        ui.setconfig('ui', 'nontty', 'true', 'hgwebdir')
        ui.setconfig("web", "baseurl", "/hg", "hgwebdir")
        ui.setconfig("web", "style", "gitweb", "hgwebdir")
        ui.setconfig("web", "logourl", "http://nocproject.org/", "hgwebdir")
        hg_paths = [
            ("noc", ".")
        ]
        hg_wsgi = tornado.wsgi.WSGIContainer(hgwebdir(hg_paths, ui))

        vi = sys.version_info

        application = tornado.web.Application([
            # /static/
            (r"^/static/(.*)", tornado.web.StaticFileHandler, {
                "path": "static"}),
            # /media/
            (r"^/media/(.*)", tornado.web.StaticFileHandler, {
                "path": "lib/python%d.%d/site-packages/django/contrib/admin/static" % (vi[0], vi[1])
            }),
            # NOC application's js, img and css files
            # @todo: write proper static handler
            (r"(/[^/]+/[^/]+/(?:js|img|css)/.+)", AppStaticFileHandler, {
                "path": self.prefix}),
            # / -> /main/desktop/
            (r"^/$", tornado.web.RedirectHandler, {"url": "/main/desktop/"}),
            # Serve mercurial repo
            (r"^/hg/static/(.*)", tornado.web.StaticFileHandler, {
                "path": "lib/python%d.%d/site-packages/mercurial/templates/static" % (vi[0], vi[1])
            }),
            (r"^/hg.*$", HGHandler, {"fallback": hg_wsgi}),
            # Pass to NOC
            (r"^.*$", AppHandler, {"fallback": noc_wsgi})
        ])
        self.logger.info("Running NOC %s webserver" % get_version())
        self.logger.info("Loading site")
        self.logger.info("Listening %s:%s" % (address, port))
        # Create tornado server
        self.server = tornado.httpserver.HTTPServer(application)
        try:
            self.server.bind(port, address)
        except socket.error, why:
            self.logger.error("Unable to bind socket: %s", why)
            os._exit(1)
        # Run children
        nc = self.config.getint("web", "workers")
        if nc == 0:
            nc = cpu_count()
        self.t_children = {}  # pid -> id
        ids = set(range(nc))
        while True:
            # Run children
            while len(self.t_children) < nc:
                c_id = ids.pop()
                pid = os.fork()
                if pid == 0:
                    self.children_loop(c_id)
                elif pid < 0:
                    self.logger.error("Unable to fork child")
                else:
                    self.logger.info("Running child PID %d (id %s)", pid, c_id)
                    self.t_children[pid] = c_id
            # Wait for status
            try:
                pid, status = os.wait()
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                raise
            if pid not in self.t_children:
                continue
            ids.add(self.t_children[pid])
            del self.t_children[pid]
            self.logger.info("Exiting child %d" % pid)

    def children_loop(self, c_id):
        # Redefine metrics
        self.metrics = MetricsHub(
            "noc.%s.%s.%s." % (self.daemon_name, self.instance_id, c_id),
            *self.METRICS)
        self.t_children = None
        # Initialize pending sockets
        sockets = self.server._pending_sockets
        self.server._pending_sockets = []
        self.server.add_sockets(sockets)
        # Connect to mongodb
        import noc.lib.nosql
        # Initialize site
        self.logger.info("Registering web applications")
        from noc.lib.app import site
        site.autodiscover()
        # Run children's I/O loop
        dt = (time.time() - self.start_time) * 1000
        self.logger.info("Starting to serve requests (in %.2fms)", dt)
        run_reporter()
        tornado.ioloop.IOLoop.instance().start()

    def at_exit(self):
        if self.t_children:
            for pid in self.t_children:
                self.logger.info("Stopping child %d" % pid)
                os.kill(pid, signal.SIGTERM)
        super(Web, self).at_exit()
