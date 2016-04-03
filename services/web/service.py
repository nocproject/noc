#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Web service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

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
    process_name = "noc-%(name).10s-%(instance).2s"

    def __init__(self):
        super(WebService, self).__init__()

    def get_handlers(self):
        wsgi = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler()
        )
        return [
            # Pass to NOC
            (r"^.*$", tornado.web.FallbackHandler, {"fallback": wsgi})
        ]

    def on_activate(self):
        # Initialize site
        self.logger.info("Registering web applications")
        from noc.lib.app import site
        site.autodiscover()

if __name__ == "__main__":
    WebService().start()
