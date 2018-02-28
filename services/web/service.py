#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Web service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.web
import tornado.httpserver
import tornado.gen
import tornado.wsgi
import django.core.handlers.wsgi
from tornado import escape
from tornado import httputil
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.main.models.customfield import CustomField
from noc.core.perf import metrics


class WebService(Service):
    name = "web"
    api = []
    use_translation = True
    if config.features.traefik:
        traefik_backend = "web"
        traefik_frontend_rule = "PathPrefix:/"

    def __init__(self):
        super(WebService, self).__init__()

    def get_handlers(self):
        return [
            # Pass to NOC
            (r"^.*$", NOCWSGIHandler, {"service": self})
        ]

    def on_activate(self):
        # Initialize audit trail
        from noc.main.models.audittrail import AuditTrail
        AuditTrail.install()
        # Initialize site
        self.logger.info("Registering web applications")
        from noc.lib.app.site import site
        site.service = self
        site.autodiscover()
        # Install Custom fields
        CustomField.install_fields()

    def get_backend_weight(self):
        return config.web.max_threads

    def get_backend_limit(self):
        return config.web.max_threads


class NOCWSGIHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service
        self.executor = self.service.get_executor("max")
        self.backend_id = "%s (%s:%s)" % (
            self.service.service_id,
            self.service.address, self.service.port)

    @tornado.gen.coroutine
    def prepare(self):
        data = yield self.process_request(self.request)
        header_obj = httputil.HTTPHeaders()
        for key, value in data["headers"]:
            header_obj.add(key, value)
        self.request.connection.write_headers(
            data["start_line"], header_obj, chunk=data["body"]
        )
        self.request.connection.finish()
        self.log_request(data["status_code"], self.request)
        self._finished = True

    @tornado.gen.coroutine
    def process_request(self, request):
        data = {}
        response = []

        def start_response(status, response_headers, exc_info=None):
            data["status"] = status
            data["headers"] = response_headers
            return response.append

        if config.features.forensic:
            in_label = "%s %s %s %s" % (
                request.remote_ip,
                request.headers.get("Remote-User", "-"),
                request.method,
                request.uri
            )
        else:
            in_label = None
        wsgi = django.core.handlers.wsgi.WSGIHandler()
        app_response = yield self.executor.submit(
            wsgi,
            tornado.wsgi.WSGIContainer.environ(request),
            start_response,
            _in_label=in_label
        )
        try:
            response.extend(app_response)
            body = b"".join(response)
        finally:
            if hasattr(app_response, "close"):
                app_response.close()
        if not data:
            raise Exception("WSGI app did not call start_response")

        status_code, reason = data["status"].split(' ', 1)
        status_code = int(status_code)
        headers = data["headers"]
        header_set = set(k.lower() for (k, v) in headers)
        body = escape.utf8(body)
        if status_code != 304:
            if "content-length" not in header_set:
                headers.append(("Content-Length", str(len(body))))
            if "content-type" not in header_set:
                headers.append(("Content-Type", "text/html; charset=UTF-8"))
        if "server" not in header_set:
            headers.append(("Server", "TornadoServer/%s" % tornado.version))
        headers.append(("X-NOC-Backend", self.backend_id))
        data["status_code"] = status_code
        data["start_line"] = httputil.ResponseStartLine("HTTP/1.1", status_code, reason)
        data["body"] = body
        raise tornado.gen.Return(data)

    def log_request(self, status_code, request):
        method = request.method
        uri = request.uri
        remote_ip = request.remote_ip
        user = request.headers.get("Remote-User", "-")
        agent = request.headers.get("User-Agent", "-")
        referer = request.headers.get("Referer", "-")
        self.service.logger.info(
            "%s %s - \"%s %s\" HTTP/1.1 %s \"%s\" %s %.2fms",
            remote_ip, user, method, uri, status_code,
            referer, agent,
            1000.0 * request.request_time()
        )
        metrics["http_requests"] += 1
        metrics["http_requests_%s" % method.lower()] += 1
        metrics["http_response_%s" % status_code] += 1


if __name__ == "__main__":
    WebService().start()
