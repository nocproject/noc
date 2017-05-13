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
from noc.main.models.customfield import CustomField
from noc.core.perf import metrics


class WebService(Service):
    name = "web"
    api = []
    process_name = "noc-%(name).10s-%(instance).3s"
    use_translation = True
    traefik_backend = "web"
    traefik_frontend_rule = "PathPrefix:/"

    def __init__(self):
        super(WebService, self).__init__()

    def get_handlers(self):
        wsgi = NOCWSGIContainer(
            self,
            django.core.handlers.wsgi.WSGIHandler()
        )
        return [
            # Pass to NOC
            (r"^.*$", tornado.web.FallbackHandler, {"fallback": wsgi})
        ]

    def on_activate(self):
        # Initialize site
        self.logger.info("Registering web applications")
        from noc.lib.app.site import site
        site.service = self
        site.autodiscover()
        # Install Custom fields
        CustomField.install_fields()


class NOCWSGIContainer(tornado.wsgi.WSGIContainer):
    def __init__(self, service, wsgi):
        super(NOCWSGIContainer, self).__init__(wsgi)
        self.service = service

    def _log(self, status_code, request):
        method = request.method
        uri = request.uri
        remote_ip = request.remote_ip
        self.service.logger.info(
            "%s %s (%s) %.2fms",
            method, uri, remote_ip,
            1000.0 * request.request_time()
        )
        metrics["http_requests"] += 1
        metrics["http_requests_%s" % method.lower()] += 1
        metrics["http_response_%s" % status_code] += 1


if __name__ == "__main__":
    WebService().start()
